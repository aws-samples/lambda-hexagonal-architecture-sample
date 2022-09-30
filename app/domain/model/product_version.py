from typing import Optional

from pydantic import BaseModel, Field


class ProductVersion(BaseModel):
    id: str = Field(..., title="Id")
    name: Optional[str] = Field(title="Name")
    version: str = Field(..., title="Version")
    createDate: str = Field(..., title="CreateDate")
