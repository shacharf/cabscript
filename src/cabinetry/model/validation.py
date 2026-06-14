from enum import Enum
from pydantic import BaseModel


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class ValidationMessage(BaseModel):
    severity: Severity
    code: str
    message: str
    path: str | None = None
