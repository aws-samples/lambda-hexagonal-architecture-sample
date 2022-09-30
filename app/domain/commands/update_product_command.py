from typing import Optional

from pydantic import BaseModel


class UpdateProductCommand(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
