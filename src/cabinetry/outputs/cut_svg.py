"""Render a saw-cut plan for a single stock board as an SVG string."""

from __future__ import annotations

from html import escape

from .nesting import Board

SCALE = 0.2  # mm to px
PAD = 30


def board_to_svg(board: Board) -> str:
    """Render one nested board with labeled part rectangles and dimensions."""
    bw = board.board_w * SCALE
    bh = board.board_h * SCALE

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{bw + 2 * PAD:.0f}" height="{bh + 2 * PAD:.0f}" '
        f'viewBox="{-PAD} {-PAD} {bw + 2 * PAD:.0f} {bh + 2 * PAD:.0f}" '
        f'font-family="sans-serif">',
        f'<rect x="0" y="0" width="{bw:.1f}" height="{bh:.1f}" '
        f'fill="#fdfcf8" stroke="#333" stroke-width="2"/>',
        f'<text x="0" y="-12" font-size="14" fill="#333">'
        f'Board {board.index} — {escape(board.material)} '
        f'{board.thickness:g}mm — {board.board_w:g}×{board.board_h:g} '
        f'(waste {board.waste_pct:.0f}%)</text>',
    ]

    for p in board.placements:
        x = p.x * SCALE
        y = p.y * SCALE
        w = p.w * SCALE
        h = p.h * SCALE
        cx = x + w / 2
        cy = y + h / 2
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="#cfe2f3" stroke="#2a5d8f" stroke-width="1"/>'
        )
        label = escape(p.label) + (" ⟲" if p.rotated else "")
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 4:.1f}" font-size="11" '
            f'text-anchor="middle" fill="#10324f">{label}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 10:.1f}" font-size="10" '
            f'text-anchor="middle" fill="#456">{p.w:g}×{p.h:g}</text>'
        )
        if p.formica_side:
            parts.append(
                f'<text x="{cx:.1f}" y="{cy + 22:.1f}" font-size="8" '
                f'text-anchor="middle" fill="#a55">F: {escape(p.formica_side)}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
