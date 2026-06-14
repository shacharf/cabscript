from pydantic import BaseModel
from .primitives import Mm


class DoorSpec(BaseModel):
    style: str = "slab"
    hinges: str = "concealed"
    top: str = "auto"
    main: str = "auto"
