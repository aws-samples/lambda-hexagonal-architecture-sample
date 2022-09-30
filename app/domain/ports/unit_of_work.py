import typing
from abc import ABC, abstractmethod

from app.domain.model import product, product_version


class ProductsRepository(ABC):
    @abstractmethod
    def add(self, product: product.Product) -> None:
        ...

    @abstractmethod
    def update_attributes(self, product_id: str, **kwargs) -> None:
        ...

    @abstractmethod
    def get(self, product_id: str) -> typing.Optional[product.Product]:
        ...

    @abstractmethod
    def delete(self, product_id: str) -> None:
        ...


class ProductVersionsRepository(ABC):
    @abstractmethod
    def add(
        self, product_id: str, product_version: product_version.ProductVersion
    ) -> None:
        ...

    @abstractmethod
    def get(
        self, product_id: str, product_version_id: str
    ) -> typing.Optional[product_version.ProductVersion]:
        ...


class UnitOfWork(ABC):
    products: ProductsRepository
    product_versions: ProductVersionsRepository

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def __enter__(self) -> typing.Any:
        ...

    @abstractmethod
    def __exit__(self, *args) -> None:
        ...
