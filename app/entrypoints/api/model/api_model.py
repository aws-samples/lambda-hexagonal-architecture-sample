from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GetProductResponse(BaseModel):
    id: str = Field(..., title="Id")
    name: str = Field(..., title="Name")
    description: Optional[str] = Field(title="Description")
    createDate: str = Field(..., title="CreateDate")
    lastUpdateDate: str = Field(..., title="LastUpdateDate")


class CreateProductRequest(BaseModel):
    name: str = Field(..., title="Name")
    description: Optional[str] = Field(title="Description")


class CreateProductResponse(BaseModel):
    id: str = Field(..., title="Id")


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(title="Name")
    description: Optional[str] = Field(title="Description")


class UpdateProductResponse(BaseModel):
    id: str = Field(..., title="Id")


class DeleteProductResponse(BaseModel):
    id: str = Field(..., title="Id")


class Product(BaseModel):
    id: str = Field(..., title="Id")
    name: str = Field(..., title="Name")
    description: Optional[str] = Field(title="Description")
    createDate: str = Field(..., title="CreateDate")
    lastUpdateDate: str = Field(..., title="LastUpdateDate")


class ListProductsResponse(BaseModel):
    nextToken: Optional[Dict[str, Any]] = Field(title="LastEvaluatedKey token")
    products: List[Product] = Field(..., title="Products")
