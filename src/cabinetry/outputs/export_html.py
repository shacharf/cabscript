"""Generate a self-contained single-page HTML report of the fabrication export."""

from __future__ import annotations

import csv
import io
from html import escape

from .cutlist import CutListItem, board_cutlist_to_csv
from .cut_svg import board_to_svg
from .nesting import Board
from ..model.project import ResolvedProject
from .view2d_svg import project_to_svg


def _csv_to_table(csv_str: str, title: str) -> str:
    rows = list(csv.reader(io.StringIO(csv_str)))
    if not rows:
        return ""
    header, *data = rows
    th = "".join(f"<th>{escape(c)}</th>" for c in header)
    tbody = ""
    for row in data:
        td = "".join(f"<td>{escape(c)}</td>" for c in row)
        tbody += f"<tr>{td}</tr>\n"
    return (
        f"<section>\n<h2>{escape(title)}</h2>\n"
        f"<table>\n<thead><tr>{th}</tr></thead>\n"
        f"<tbody>{tbody}</tbody>\n</table>\n</section>\n"
    )


def build_export_html(
    items: list[CutListItem],
    boards: list[Board],
    cut_plan_csv: str,
    project: ResolvedProject | None = None,
) -> str:
    cut_list_csv = board_cutlist_to_csv(items)

    view2d_section = ""
    if project is not None:
        svg = project_to_svg(project)
        view2d_section = (
            f'<section id="view2d">\n'
            f'<h2>Cabinet View</h2>\n'
            f'<div class="view2d-wrap">{svg}</div>\n'
            f'</section>\n'
        )

    board_svgs = ""
    for board in boards:
        svg = board_to_svg(board)
        board_svgs += (
            f'<div class="board-wrap">\n'
            f'<h3>Board {board.index} — {escape(board.material)} '
            f'{board.thickness:g}mm &nbsp; '
            f'<span class="waste">waste {board.waste_pct:.0f}%</span></h3>\n'
            f'{svg}\n</div>\n'
        )

    cut_list_table = _csv_to_table(cut_list_csv, "Cut List")
    cut_plan_table = _csv_to_table(cut_plan_csv, "Cut Plan (placements)")

    total_boards = len(boards)
    avg_waste = (
        sum(b.waste_pct for b in boards) / total_boards if total_boards else 0.0
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cabinet Export</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, sans-serif; margin: 0; padding: 24px; background: #f5f4f0; color: #222; }}
  h1 {{ margin: 0 0 4px; font-size: 1.6rem; }}
  .meta {{ color: #666; font-size: .9rem; margin-bottom: 32px; }}
  h2 {{ font-size: 1.15rem; border-bottom: 2px solid #c8b89a; padding-bottom: 6px; margin-bottom: 12px; }}
  h3 {{ font-size: 1rem; margin: 20px 0 6px; color: #2a4; }}
  section {{ margin-bottom: 40px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: .85rem; background: #fff; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 4px #0001; }}
  th {{ background: #3a3028; color: #fff; padding: 7px 10px; text-align: left; white-space: nowrap; }}
  td {{ padding: 5px 10px; border-bottom: 1px solid #e8e4dc; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:nth-child(even) td {{ background: #faf9f6; }}
  .boards-grid {{ display: flex; flex-wrap: wrap; gap: 24px; }}
  .board-wrap {{ background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px #0001; max-width: 100%; overflow: auto; }}
  .board-wrap svg {{ max-width: 100%; height: auto; display: block; }}
  .waste {{ color: #c55; font-weight: normal; font-size: .9em; }}
  .view2d-wrap {{ background: #0d1525; border-radius: 8px; padding: 16px; display: inline-block; max-width: 100%; overflow: auto; }}
  .view2d-wrap svg {{ display: block; max-width: 100%; height: auto; }}
  nav {{ position: sticky; top: 0; background: #3a3028; color: #fff; padding: 10px 24px; margin: -24px -24px 32px; display: flex; gap: 20px; font-size: .9rem; z-index: 10; }}
  nav a {{ color: #f0e8d8; text-decoration: none; }} nav a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<nav>
  <strong style="margin-right:12px">Cabinet Export</strong>
  {'<a href="#view2d">View</a>' if view2d_section else ''}
  <a href="#cut-list">Cut List</a>
  <a href="#boards">Boards ({total_boards})</a>
  <a href="#cut-plan">Cut Plan</a>
</nav>
<h1>Fabrication Export</h1>
<p class="meta">{total_boards} board{'s' if total_boards != 1 else ''} &middot; avg waste {avg_waste:.0f}%</p>

{view2d_section}
<section id="cut-list">
{cut_list_table}
</section>

<section id="boards">
<h2>Board Layouts</h2>
<div class="boards-grid">
{board_svgs}
</div>
</section>

<section id="cut-plan">
{cut_plan_table}
</section>
</body>
</html>"""
