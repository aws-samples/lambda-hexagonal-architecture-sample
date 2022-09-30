import enum
import typing

from mypy_boto3_dynamodb import client

from app.adapters.internal import dynamodb_base
from app.domain.model import product, product_version
from app.domain.ports import unit_of_work


class DBPrefix(enum.Enum):
    PRODUCT = "PRODUCT"
    PRODUCT_VERSION = "PRODUCTVERSION"


class DynamoDBProductsRepository(
    dynamodb_base.DynamoDBRepository, unit_of_work.ProductsRepository
):
    """Products DynamoDB repository."""

    def __init__(self, table_name, context: dynamodb_base.DynamoDBContext):
        super().__init__(table_name, context)

    def add(self, product: product.Product) -> None:
        """Adds a product to the DynamoDB table."""
        self.add_generic_item(
            item=product.dict(), key=self.generate_product_key(product_id=product.id)
        )

    def get(self, product_id: str) -> typing.Optional[product.Product]:
        """Gets a product from the DynamoDB table."""
        key = self.generate_product_key(product_id)
        request = self._create_get_request(key)
        product_dict = self._context.get_generic_item(request)
        return (
            product.Product.parse_obj(product_dict)
            if product_dict is not None
            else None
        )

    def update_attributes(self, product_id: str, **kwargs) -> None:
        """Updates arbitraty attributes of the product in DynamoDB table."""
        update_expression_setters = [
            f"{key}=:p{idx}" for idx, (key, value) in enumerate(kwargs.items())
        ]
        update_values = {
            f":p{idx}": value for idx, (key, value) in enumerate(kwargs.items())
        }
        self.update_generic_item(
            expression={
                "UpdateExpression": f"set {', '.join(update_expression_setters)}",
                "ExpressionAttributeValues": update_values,
                "ConditionExpression": "(attribute_exists(PK) AND attribute_exists(SK))",
            },
            key=self.generate_product_key(product_id=product_id),
        )

    def delete(self, product_id: str) -> None:
        key = self.generate_product_key(product_id)
        self.delete_generic_item(key=key)

    @staticmethod
    def generate_product_key(product_id: str) -> dict:
        """Generates primary key for product entity."""
        return {
            "PK": f"{DBPrefix.PRODUCT.value}#{product_id}",
            "SK": f"{DBPrefix.PRODUCT.value}#{product_id}",
        }


class DynamoDBProductVersionsRepository(
    dynamodb_base.DynamoDBRepository, unit_of_work.ProductVersionsRepository
):
    """Product version DynamoDB repository."""

    def __init__(self, table_name: str, context: dynamodb_base.DynamoDBContext):
        super().__init__(table_name, context)

    def add(
        self, product_id: str, product_version: product_version.ProductVersion
    ) -> None:
        """Adds a product version to the DynamoDB table."""
        self.add_generic_item(
            item=product_version.dict(),
            key=self.generate_product_version_key(
                product_id=product_id, version_id=product_version.id
            ),
        )

    def get(
        self, product_id: str, version_id: str
    ) -> typing.Optional[product_version.ProductVersion]:
        """Gets a product version from the DynamoDB table."""
        key = self.generate_product_version_key(product_id, version_id)
        request = self._create_get_request(key)
        product_version_dics = self._context.get_generic_item(request)
        return (
            product_version.ProductVersion.parse_obj(product_version_dics)
            if product_version_dics is not None
            else None
        )

    @staticmethod
    def generate_product_version_key(product_id: str, version_id: str):
        """Generates primary key for product version entity."""
        return {
            "PK": f"{DBPrefix.PRODUCT.value}#{product_id}",
            "SK": f"{DBPrefix.PRODUCT_VERSION.value}#{version_id}",
        }


class DynamoDBUnitOfWork(unit_of_work.UnitOfWork):
    """Repository provider and unit of work for DynamoDB."""

    products: DynamoDBProductsRepository
    product_versions: DynamoDBProductVersionsRepository

    def __init__(self, table_name: str, dynamodb_client: client.DynamoDBClient):
        self._dynamo_db_client = dynamodb_client
        self._table_name = table_name
        self._context: typing.Optional[dynamodb_base.DynamoDBContext] = None

    def commit(self) -> None:
        """Commits up to 25 changes to the DynamoDB table in a single transaction."""
        if self._context:
            self._context.commit()

    def __enter__(self) -> typing.Any:
        self._context = dynamodb_base.DynamoDBContext(
            dynamodb_client=self._dynamo_db_client
        )
        self.products = DynamoDBProductsRepository(
            table_name=self._table_name, context=self._context
        )
        self.product_versions = DynamoDBProductVersionsRepository(
            table_name=self._table_name, context=self._context
        )

        return self

    def __exit__(self, *args) -> None:
        self._context = None
        self.products = None  # type: ignore
        self.product_versions = None  # type: ignore
