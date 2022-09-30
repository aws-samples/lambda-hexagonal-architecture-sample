from pydantic import BaseModel


class DeleteProductCommand(BaseModel):
    id: str
