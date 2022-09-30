from typing import Optional

from pydantic import BaseModel


class CreateProductCommand(BaseModel):
    name: str
    description: Optional[str]
