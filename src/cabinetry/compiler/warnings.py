from .context import CompileContext
from ..model.parts import Part


def check_parts(ctx: CompileContext, parts: list[Part]) -> None:
    max_board = ctx.material.max_board.length
    for part in parts:
        if part.length > max_board:
            ctx.warn(
                "BOARD_TOO_LONG",
                f"Part {part.id} ({part.name}) length {part.length}mm exceeds "
                f"max board length {max_board}mm.",
                path=part.id,
            )
