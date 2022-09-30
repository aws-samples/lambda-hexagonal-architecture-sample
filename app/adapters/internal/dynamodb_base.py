from typing import Any, List

from mypy_boto3_dynamodb import client, type_defs

from app.domain.exceptions import repository_exception


class DynamoDBContext:
    """Transactional context manager for DynamoDB."""

    def __init__(self, dynamodb_client: client.DynamoDBClient):
        self._db_items: List[type_defs.TransactWriteItemTypeDef] = []
        self._dynamo_db_client = dynamodb_client

    def commit(self) -> None:
        """Commits up to 25 changes to the DynamoDB table in a single transaction."""
        try:
            self._dynamo_db_client.transact_write_items(TransactItems=self._db_items)
            self._db_items = []
        except Exception as e:
            raise repository_exception.RepositoryException(
                "Failed to commit a transaction to DynamoDB."
            ) from e

    def add_generic_item(self, item: dict) -> None:
        """Adds DynamoDB modifying instructions to a pending list."""
        dynamodb_item = type_defs.TransactWriteItemTypeDef(**item)
        self._db_items.append(dynamodb_item)

    def get_generic_item(self, request: dict) -> Any:
        """
        Gets a generic item from DynamoDB by primary key.
        Primary key must contain both partition key and sort key.
        """
        item = self._dynamo_db_client.get_item(**request)

        return item["Item"] if "Item" in item else None


class DynamoDBRepository:
    """Generic DynamoDB repository."""

    def __init__(self, table_name: str, context: DynamoDBContext):
        self._table_name = table_name
        self._context = context

    def add_generic_item(self, item: dict, key: dict) -> None:
        """
        Converts item to a DynamoDB put item instruction
        and adds to the pending transactions list.
        """
        self._context.add_generic_item(
            item=self._create_put_modifier(obj=item, key=key)
        )

    def update_generic_item(self, expression: dict, key: dict) -> None:
        """
        Converts item to a DynamoDB update instruction
        and adds to the pending transactions list.
        """
        self._context.add_generic_item(
            item=self._create_update_modifier(expression=expression, key=key)
        )

    def delete_generic_item(self, key: dict) -> None:
        """
        Converts item to a DynamoDB delete instruction
        and adds to the pending transactions list.
        """
        self._context.add_generic_item(item=self._create_delete_modifier(key=key))

    def _create_put_modifier(self, obj: dict, key: dict) -> dict:
        return {
            "Put": {
                "TableName": self._table_name,
                "Item": {**obj, **key},
                "ConditionExpression": "(attribute_not_exists(PK) AND attribute_not_exists(SK))",
            }
        }

    def _create_update_modifier(self, expression: dict, key: dict) -> dict:
        return {"Update": {"TableName": self._table_name, "Key": key, **expression}}

    def _create_get_request(self, key: dict) -> dict:
        return {"TableName": self._table_name, "Key": {**key}}

    def _create_delete_modifier(self, key: dict) -> dict:
        return {"Delete": {"TableName": self._table_name, "Key": key}}
