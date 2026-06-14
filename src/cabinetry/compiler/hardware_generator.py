import re
from .context import CompileContext
from ..model.hardware import HardwareItem
from ..model.primitives import Vec3


def generate_base_hardware(ctx: CompileContext, width: float, depth: float) -> list[HardwareItem]:
    items: list[HardwareItem] = []
    cabinet_spec = ctx.normalized_dsl.get("cabinet", {})
    base_spec = cabinet_spec.get("base")

    if base_spec is None:
        return items

    base_str = str(base_spec).strip()
    m = re.match(r"^legs\s+(\d+(?:\.\d+)?)$", base_str)
    if m:
        h = float(m.group(1))
        setback = 50.0
        positions = [
            (setback, setback),
            (width - setback, setback),
            (setback, depth - setback),
            (width - setback, depth - setback),
        ]
        for i, (x, z) in enumerate(positions):
            items.append(
                HardwareItem(
                    id=f"leg_{i + 1:03d}",
                    kind="leg",
                    name=f"Adjustable Leg {i + 1}",
                    position=Vec3(x=x, y=0.0, z=z),
                    params={"height": h},
                )
            )

    return items
