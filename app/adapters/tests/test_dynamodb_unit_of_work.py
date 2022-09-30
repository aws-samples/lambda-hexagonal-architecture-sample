import datetime
import uuid

import assertpy
import boto3
import moto
import pytest

from app.adapters import dynamodb_unit_of_work
from app.domain.model import product

TEST_TABLE_NAME = "test-table"


@pytest.fixture
def mock_dynamodb():
    with moto.mock_dynamodb():
        yield boto3.resource("dynamodb", region_name="eu-central-1")


@pytest.fixture(autouse=True)
def app_registry_dynamodb_table(mock_dynamodb):
    table = mock_dynamodb.create_table(
        TableName="test-table",
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},
            {"AttributeName": "SK", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    table.meta.client.get_waiter("table_exists").wait(TableName="test-table")
    return table


def test_add_and_commit_should_store_product(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    unit_of_work_readonly = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_product_id = str(uuid.uuid4())
    new_product = product.Product(
        id=new_product_id,
        name="test-name",
        description="test-description",
        createDate=current_time,
        lastUpdateDate=current_time,
    )

    # Act
    with unit_of_work:
        unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Assert
    with unit_of_work_readonly:
        product_from_db = unit_of_work_readonly.products.get(new_product_id)

    assertpy.assert_that(product_from_db).is_not_none()
    assertpy.assert_that(product_from_db.dict()).is_equal_to(
        {
            "id": new_product_id,
            "name": "test-name",
            "description": "test-description",
            "createDate": current_time,
            "lastUpdateDate": current_time,
        }
    )


def test_get_product_when_does_not_exist_should_throw(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )

    # Act
    with unit_of_work:
        product = unit_of_work.products.get("does-not-exist")

    # Assert
    assertpy.assert_that(product).is_none()


def test_update_attribute_should_only_update_specified_property(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    unit_of_work_readonly = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_product_id = str(uuid.uuid4())
    new_product = product.Product(
        id=new_product_id,
        name="test-name",
        description="test-description",
        createDate=current_time,
        lastUpdateDate=current_time,
    )
    with unit_of_work:
        unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Act
    with unit_of_work:
        unit_of_work.products.update_attributes(
            new_product_id, description="new-description"
        )
        unit_of_work.commit()

    # Assert
    with unit_of_work_readonly:
        product_from_db = unit_of_work_readonly.products.get(new_product_id)

    assertpy.assert_that(product_from_db).is_not_none()
    assertpy.assert_that(product_from_db.dict()).is_equal_to(
        {
            "id": new_product_id,
            "name": "test-name",
            "description": "new-description",
            "createDate": current_time,
            "lastUpdateDate": current_time,
        }
    )


def test_delete_and_commit_should_delete_product(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    unit_of_work_readonly = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_product_id = str(uuid.uuid4())
    new_product = product.Product(
        id=new_product_id,
        name="test-name",
        description="test-description",
        createDate=current_time,
        lastUpdateDate=current_time,
    )
    with unit_of_work:
        unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Act
    with unit_of_work:
        unit_of_work.products.delete(new_product_id)
        unit_of_work.commit()

    # Assert
    with unit_of_work_readonly:
        product_from_db = unit_of_work_readonly.products.get(new_product_id)

    assertpy.assert_that(product_from_db).is_none()
