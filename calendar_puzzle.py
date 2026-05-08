# -*- coding: utf-8 -*-
import argparse


BOARD = set(
    (r, c)
    for r in range(7)
    for c in range(8)
    if not (r == 6 and c < 5)
)

PIECES = [
    {"name": "I", "shape": {(0, 0), (0, 1), (0, 2), (0, 3)}},
    {"name": "U", "shape": {(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)}},
    {"name": "T", "shape": {(0, 0), (0, 1), (0, 2), (1, 1)}},
    {"name": "O", "shape": {(0, 0), (0, 1), (1, 0), (1, 1)}},
    {"name": "V", "shape": {(0, 0), (0, 1), (1, 0)}},
    {"name": "L", "shape": {(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)}},
    {"name": "P", "shape": {(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)}},
    {"name": "S", "shape": {(0, 0), (1, 0), (1, 1), (2, 1)}},
    {"name": "Y", "shape": {(0, 0), (0, 1), (0, 2), (0, 3), (1, 2)}},
    {"name": "F", "shape": {(0, 0), (0, 1), (0, 2), (1, 0)}},
    {"name": "J", "shape": {(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)}},
]

WEEKDAY_MAP = {
    0: (1, 3),
    1: (0, 1),
    2: (0, 2),
    3: (0, 3),
    4: (1, 0),
    5: (1, 1),
    6: (1, 2),
}

WEEKDAY_NAMES = {
    0: "周日",
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
}

PIECE_SYMBOLS = {
    "I": "🟥",
    "U": "🟧",
    "T": "🟨",
    "O": "🟩",
    "V": "🟦",
    "L": "🟪",
    "P": "🟫",
    "S": "⬛",
    "Y": "⬜",
    "F": "⚫",
    "J": "⚪",
    "*": "·",
}


def rotations(piece):
    results = []
    current = piece
    for _ in range(4):
        current = {(c, -r) for r, c in current}
        min_r = min(r for r, c in current)
        min_c = min(c for r, c in current)
        current = {(r - min_r, c - min_c) for r, c in current}
        results.append(current)
    return results


def reflections(piece):
    reflected = {(r, -c) for r, c in piece}
    min_c = min(c for r, c in reflected)
    return {(r, c - min_c) for r, c in reflected}


def all_variants(piece):
    variants = set()
    for rotated in rotations(piece):
        variants.add(frozenset(rotated))
        variants.add(frozenset(reflections(rotated)))
    return [set(variant) for variant in variants]


def get_day_position(day):
    if day <= 4:
        return 2, day - 1
    if day <= 28:
        return 2 + (day - 1) // 8, (day - 5) % 8
    if day == 29:
        return 6, 5
    if day == 30:
        return 6, 6
    return 6, 7


def get_empty_cells(month, day, weekday):
    weekday_pos = WEEKDAY_MAP[weekday]
    month_pos = ((month - 1) // 4, 4 + (month - 1) % 4)
    day_pos = get_day_position(day)
    return {weekday_pos, month_pos, day_pos}


def placements(piece, board_cells):
    results = []
    for variant in all_variants(piece["shape"]):
        max_r = max(r for r, c in variant)
        max_c = max(c for r, c in variant)
        for dr in range(7 - max_r):
            for dc in range(8 - max_c):
                placed = {(r + dr, c + dc) for r, c in variant}
                if placed <= board_cells:
                    results.append((piece["name"], placed))
    return results


class DLXNode:
    def __init__(self):
        self.L = self.R = self.U = self.D = self.C = self
        self.row_id = None
        self.col_id = None
        self.size = 0


class DLX:
    def __init__(self, matrix, max_solutions=None):
        self.header = DLXNode()
        self.columns = []
        self.solution = []
        self.solutions = []
        self.max_solutions = max_solutions

        if not matrix:
            return

        last = self.header
        for col_index in range(len(matrix[0])):
            column = DLXNode()
            column.col_id = col_index
            column.U = column.D = column
            column.L = last
            column.R = self.header
            last.R = column
            self.header.L = column
            self.columns.append(column)
            last = column

        for row_index, row in enumerate(matrix):
            previous = None
            for col_index, value in enumerate(row):
                if not value:
                    continue
                node = DLXNode()
                node.row_id = row_index
                node.col_id = col_index
                column = self.columns[col_index]
                node.U = column.U
                node.D = column
                column.U.D = node
                column.U = node
                node.C = column
                column.size += 1
                if previous is None:
                    node.L = node.R = node
                else:
                    node.L = previous
                    node.R = previous.R
                    previous.R.L = node
                    previous.R = node
                previous = node

    def cover(self, column):
        column.R.L = column.L
        column.L.R = column.R
        row = column.D
        while row != column:
            node = row.R
            while node != row:
                node.D.U = node.U
                node.U.D = node.D
                node.C.size -= 1
                node = node.R
            row = row.D

    def uncover(self, column):
        row = column.U
        while row != column:
            node = row.L
            while node != row:
                node.C.size += 1
                node.D.U = node
                node.U.D = node
                node = node.L
            row = row.U
        column.R.L = column
        column.L.R = column

    def search(self):
        if self.max_solutions and len(self.solutions) >= self.max_solutions:
            return
        if self.header.R == self.header:
            self.solutions.append(list(self.solution))
            return

        chosen = self.header.R
        candidate = chosen.R
        while candidate != self.header:
            if candidate.size < chosen.size:
                chosen = candidate
            candidate = candidate.R

        self.cover(chosen)
        row = chosen.D
        while row != chosen:
            self.solution.append(row.row_id)
            node = row.R
            while node != row:
                self.cover(node.C)
                node = node.R

            self.search()

            node = row.L
            while node != row:
                self.uncover(node.C)
                node = node.L
            self.solution.pop()
            row = row.D
        self.uncover(chosen)


def build_exact_cover(month, day, weekday):
    empty_cells = get_empty_cells(month, day, weekday)
    board_cells = BOARD - empty_cells
    all_placements = [placements(piece, board_cells) for piece in PIECES]

    columns = list(board_cells) + [piece["name"] for piece in PIECES]
    col_index = {column: index for index, column in enumerate(columns)}

    matrix = []
    row_info = []
    for placement_list in all_placements:
        for name, cells in placement_list:
            row = [0] * len(columns)
            for cell in cells:
                row[col_index[cell]] = 1
            row[col_index[name]] = 1
            matrix.append(row)
            row_info.append((name, cells))

    return matrix, row_info, empty_cells


def solve_puzzle(month, day, weekday, max_solutions=None):
    matrix, row_info, empty_cells = build_exact_cover(month, day, weekday)
    dlx = DLX(matrix, max_solutions=max_solutions)
    dlx.search()
    return dlx.solutions, row_info, empty_cells


def render_solution(solution, row_info, empty_cells):
    board = [["*" for _ in range(8)] for _ in range(7)]
    for row_id in solution:
        name, cells = row_info[row_id]
        for row, col in cells:
            board[row][col] = name
    for row, col in empty_cells:
        board[row][col] = "*"
    return [" ".join(line) for line in board]


def render_solution_with_symbols(solution, row_info, empty_cells):
    board = [["*" for _ in range(8)] for _ in range(7)]
    for row_id in solution:
        name, cells = row_info[row_id]
        for row, col in cells:
            board[row][col] = PIECE_SYMBOLS[name]
    for row, col in empty_cells:
        board[row][col] = PIECE_SYMBOLS["*"]
    return [" ".join(line) for line in board]


def format_solutions(solutions, row_info, empty_cells):
    if not solutions:
        return "此拼圖無解"

    blocks = []
    for index, solution in enumerate(solutions, 1):
        lines = [f"=== 解 {index} ==="]
        lines.extend(render_solution(solution, row_info, empty_cells))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def format_solutions_with_symbols(solutions, row_info, empty_cells):
    if not solutions:
        return "此拼圖無解"

    blocks = []
    for index, solution in enumerate(solutions, 1):
        lines = [f"=== 解 {index} ==="]
        lines.extend(render_solution_with_symbols(solution, row_info, empty_cells))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def validate_inputs(month, day, weekday, mode, max_solutions):
    if not 1 <= month <= 12:
        raise ValueError("月份必須介於 1 到 12 之間。")
    if not 1 <= day <= 31:
        raise ValueError("日期必須介於 1 到 31 之間。")
    if not 0 <= weekday <= 6:
        raise ValueError("星期必須介於 0 到 6 之間。")
    if mode not in (1, 2):
        raise ValueError("模式只能是 1 或 2。")
    if mode == 1 and (max_solutions is None or max_solutions < 1):
        raise ValueError("列出解法模式下，max_solutions 必須大於等於 1。")


def parse_args():
    parser = argparse.ArgumentParser(description="日曆拼圖 DLX 求解器")
    parser.add_argument("--month", type=int, help="月份，1 到 12")
    parser.add_argument("--day", type=int, help="日期，1 到 31")
    parser.add_argument("--weekday", type=int, help="星期，0=周日，1=周一，...，6=周六")
    parser.add_argument(
        "--mode",
        type=int,
        choices=(1, 2),
        help="1=列出解法，2=計算解數量",
    )
    parser.add_argument(
        "--max-solutions",
        type=int,
        dest="max_solutions",
        help="列出解法時，最多輸出幾組解",
    )
    return parser.parse_args()


def prompt_for_missing_inputs(args):
    month = args.month if args.month is not None else int(input("請輸入月份 (1~12): "))
    day = args.day if args.day is not None else int(input("請輸入日期 (1~31): "))
    weekday = (
        args.weekday
        if args.weekday is not None
        else int(input("請輸入星期 (0=周日,1=周一,...6=周六): "))
    )
    mode = args.mode if args.mode is not None else int(input("請選模式 (1=列出解法, 2=計算解數量): "))

    max_solutions = args.max_solutions
    if mode == 1 and max_solutions is None:
        max_solutions = int(input("請輸入想要的解數量: "))

    return month, day, weekday, mode, max_solutions


def main():
    args = parse_args()
    month, day, weekday, mode, max_solutions = prompt_for_missing_inputs(args)
    validate_inputs(month, day, weekday, mode, max_solutions)

    search_limit = max_solutions if mode == 1 else None
    solutions, row_info, empty_cells = solve_puzzle(
        month,
        day,
        weekday,
        max_solutions=search_limit,
    )

    if mode == 2:
        print("解的總數:", len(solutions))
        return

    print(format_solutions(solutions, row_info, empty_cells))


if __name__ == "__main__":
    main()
