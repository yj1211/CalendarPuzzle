# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from calendar_puzzle import (
    WEEKDAY_NAMES,
    format_first_solution_as_html_table,
    solve_puzzle,
)


README_PATH = Path("README.md")
TIMEZONE = os.getenv("CALENDAR_PUZZLE_TIMEZONE", "Asia/Taipei")
START_MARKER = "<!-- TODAY-SOLUTION-START -->"
END_MARKER = "<!-- TODAY-SOLUTION-END -->"


def build_today_section():
    now = datetime.now(ZoneInfo(TIMEZONE))
    month = now.month
    day = now.day
    weekday = (now.weekday() + 1) % 7

    solutions, row_info, empty_cells = solve_puzzle(
        month,
        day,
        weekday,
        max_solutions=1,
    )
    solution_table = format_first_solution_as_html_table(
        solutions,
        row_info,
        empty_cells,
    )

    lines = [
        START_MARKER,
        "## 今日解答",
        "",
        f"以 `{TIMEZONE}` 為準，今天是 **{month} 月 {day} 日 {WEEKDAY_NAMES[weekday]}**。",
        "",
        solution_table,
        "",
        "_此區塊由 `update_readme.py` 自動更新。_",
        END_MARKER,
    ]
    return "\n".join(lines)


def update_readme():
    content = README_PATH.read_text(encoding="utf-8")
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 or end == -1:
        raise ValueError("README.md 缺少今日解答標記區塊。")

    end += len(END_MARKER)
    updated = content[:start] + build_today_section() + content[end:]
    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
