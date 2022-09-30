from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., title="Id")
    name: str = Field(..., title="Name")
    description: Optional[str] = Field(title="Description")
    createDate: str = Field(..., title="CreateDate")
    lastUpdateDate: str = Field(..., title="LastUpdateDate")
