"""Bundle the fabrication exports (cut-list, cut-plan, board SVGs) into a ZIP."""

from __future__ import annotations

import csv
import io
import zipfile

from ..model.project import ResolvedProject
from ..stdlib.loader import StdLib
from .cutlist import generate_cutlist, board_cutlist_to_csv
from .cut_svg import board_to_svg
from .export_html import build_export_html
from .nesting import nest_parts, Board
from .view2d_svg import project_to_svg


def _cut_plan_csv(boards: list[Board]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["board_index", "label", "part_id", "x", "y", "w", "h", "rotated", "formica_side"]
    )
    for board in boards:
        for p in board.placements:
            writer.writerow(
                [
                    board.index,
                    p.label,
                    p.part_id,
                    round(p.x, 1),
                    round(p.y, 1),
                    round(p.w, 1),
                    round(p.h, 1),
                    "yes" if p.rotated else "no",
                    p.formica_side,
                ]
            )
    return output.getvalue()


def _summary_txt(boards: list[Board]) -> str:
    lines = [f"Boards required: {len(boards)}", ""]
    for board in boards:
        lines.append(
            f"Board {board.index}: {board.material} {board.thickness:g}mm "
            f"{board.board_w:g}x{board.board_h:g} — {len(board.placements)} parts, "
            f"waste {board.waste_pct:.1f}%"
        )
    return "\n".join(lines) + "\n"


def build_export_zip(
    project: ResolvedProject,
    stdlib: StdLib | None = None,
    ignore_grain: bool = False,
) -> bytes:
    """Return ZIP bytes containing cut-list.csv, cut-plan.csv and one SVG per board."""
    stdlib = stdlib or StdLib()
    items = generate_cutlist(project)
    boards = nest_parts(project, stdlib, ignore_grain=ignore_grain)

    cut_plan = _cut_plan_csv(boards)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("view2d.svg", project_to_svg(project))
        zf.writestr("cut-list.csv", board_cutlist_to_csv(items))
        zf.writestr("cut-plan.csv", cut_plan)
        zf.writestr("summary.txt", _summary_txt(boards))
        for board in boards:
            zf.writestr(f"boards/board_{board.index:02d}.svg", board_to_svg(board))
        zf.writestr("index.html", build_export_html(items, boards, cut_plan))
    return buffer.getvalue()
