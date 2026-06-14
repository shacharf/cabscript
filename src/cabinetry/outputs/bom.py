from ..model.project import ResolvedProject
from ..model.hardware import HardwareItem


def generate_bom(project: ResolvedProject) -> list[dict]:
    hardware_groups: dict[str, dict] = {}
    for hw in project.hardware:
        key = hw.kind
        if key not in hardware_groups:
            hardware_groups[key] = {"kind": hw.kind, "name": hw.name, "quantity": 0}
        hardware_groups[key]["quantity"] += 1
    return list(hardware_groups.values())
