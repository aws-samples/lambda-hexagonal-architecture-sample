from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from app.domain.model import product


class ProductsQueryService(ABC):
    @abstractmethod
    def list_products(
        self, page_size: int, next_token: Any
    ) -> Tuple[List[product.Product], Any]:
        ...

    @abstractmethod
    def get_product_by_id(self, product_id: str) -> Optional[product.Product]:
        ...
