from __future__ import annotations
from dataclasses import dataclass, field
from ..model.materials import MaterialSpec
from ..model.validation import ValidationMessage, Severity
from ..stdlib.specs import StandardSpec, DoorSystemSpec, DoorStyleSpec, ShelfSystemSpec, BaseSystemSpec
from ..stdlib.loader import StdLib


@dataclass
class CompileContext:
    raw_dsl: dict
    normalized_dsl: dict
    stdlib: StdLib
    standard: StandardSpec
    material: MaterialSpec
    door_system: DoorSystemSpec
    door_style: DoorStyleSpec
    shelf_system: ShelfSystemSpec
    base_system: BaseSystemSpec | None

    warnings: list[ValidationMessage] = field(default_factory=list)
    errors: list[ValidationMessage] = field(default_factory=list)

    def warn(self, code: str, message: str, path: str | None = None) -> None:
        self.warnings.append(
            ValidationMessage(severity=Severity.warning, code=code, message=message, path=path)
        )

    def error(self, code: str, message: str, path: str | None = None) -> None:
        self.errors.append(
            ValidationMessage(severity=Severity.error, code=code, message=message, path=path)
        )

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
