import datetime
import uuid

import assertpy
import boto3
import moto
import pytest

from app.adapters import dynamodb_query_service, dynamodb_unit_of_work
from app.domain.model import product

TEST_TABLE_NAME = "test-table"


@pytest.fixture
def mock_dynamodb():
    with moto.mock_dynamodb():
        yield boto3.resource("dynamodb", region_name="eu-central-1")


@pytest.fixture(autouse=True)
def backend_app_dynamodb_table(mock_dynamodb):
    table = mock_dynamodb.create_table(
        TableName=TEST_TABLE_NAME,
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

    table.meta.client.get_waiter("table_exists").wait(TableName=TEST_TABLE_NAME)
    return table


def test_list_products_return_all_products(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    query_service = dynamodb_query_service.DynamoDBProductsQueryService(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    product_count = 5
    product_ids = [str(uuid.uuid4()) for i in range(product_count)]

    with unit_of_work:
        for i in range(product_count):
            new_product = product.Product(
                id=product_ids[i],
                name="test-name",
                description="test-description",
                createDate=current_time,
                lastUpdateDate=current_time,
            )
            unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Act
    products, last_evaluated_key = query_service.list_products(
        page_size=product_count * 2, next_token=None
    )

    # Assert
    assertpy.assert_that(products).is_not_none()
    assertpy.assert_that(products).is_length(product_count)
    assertpy.assert_that(sorted([product.id for product in products])).is_equal_to(
        sorted(product_ids)
    )


def test_list_products_paging(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    query_service = dynamodb_query_service.DynamoDBProductsQueryService(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    product_count = 5
    product_ids = [str(uuid.uuid4()) for i in range(product_count)]

    with unit_of_work:
        for i in range(product_count):
            new_product = product.Product(
                id=product_ids[i],
                name="test-name",
                description="test-description",
                createDate=current_time,
                lastUpdateDate=current_time,
            )
            unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Act & Assert
    last_evaluated_key = None
    for i in range(product_count):
        products, last_evaluated_key = query_service.list_products(
            page_size=1, next_token=last_evaluated_key
        )
        assertpy.assert_that(products).is_not_none()
        assertpy.assert_that(products).is_length(1)
        assertpy.assert_that(products[0].id).is_in(*product_ids)


def test_get_product_by_id_returns_product(mock_dynamodb):
    # Arrange
    unit_of_work = dynamodb_unit_of_work.DynamoDBUnitOfWork(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    query_service = dynamodb_query_service.DynamoDBProductsQueryService(
        table_name=TEST_TABLE_NAME, dynamodb_client=mock_dynamodb.meta.client
    )
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    product_id = str(uuid.uuid4())

    with unit_of_work:
        new_product = product.Product(
            id=product_id,
            name="test-name",
            description="test-description",
            createDate=current_time,
            lastUpdateDate=current_time,
        )
        unit_of_work.products.add(new_product)
        unit_of_work.commit()

    # Act
    product_response = query_service.get_product_by_id(product_id=product_id)

    # Assert
    assertpy.assert_that(product_response).is_not_none()
    assertpy.assert_that(product_response.id).is_equal_to(product_id)
