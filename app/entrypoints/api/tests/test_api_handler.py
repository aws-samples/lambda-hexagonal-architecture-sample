import json
import unittest
from dataclasses import dataclass

import assertpy
import pytest
from aws_lambda_powertools.utilities.data_classes import api_gateway_proxy_event

from app.domain.command_handlers import (
    create_product_command_handler,
    delete_product_command_handler,
    update_product_command_handler,
)
from app.domain.ports import products_query_service
from app.entrypoints.api import handler
from app.entrypoints.api.model import api_model


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


def test_create_product(lambda_context):
    # Arrange
    name = "TestName"
    description = "Test description"
    request = api_model.CreateProductRequest(name=name, description=description)

    minimal_event = api_gateway_proxy_event.APIGatewayProxyEvent(
        {
            "path": "/products",
            "httpMethod": "POST",
            "requestContext": {  # correlation ID
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            },
            "body": json.dumps(request.dict()),
        }
    )

    create_product_func_mock = unittest.mock.create_autospec(
        spec=create_product_command_handler.handle_create_product_command
    )
    handler.create_product_command_handler.handle_create_product_command = (
        create_product_func_mock
    )

    # Act
    handler.handler(minimal_event, lambda_context)

    # Assert
    create_product_func_mock.assert_called_once()
    command = create_product_func_mock.call_args.kwargs["command"]
    assertpy.assert_that(command.name).is_equal_to(name)
    assertpy.assert_that(command.description).is_equal_to(description)


def test_update_product(lambda_context):
    # Arrange
    id = "test-id"
    description = "Test description"
    request = api_model.UpdateProductRequest(description=description)

    minimal_event = api_gateway_proxy_event.APIGatewayProxyEvent(
        {
            "path": f"/products/{id}",
            "httpMethod": "PUT",
            "requestContext": {  # correlation ID
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            },
            "body": json.dumps(request.dict()),
        }
    )

    update_product_func_mock = unittest.mock.create_autospec(
        spec=update_product_command_handler.handle_update_product_command
    )
    handler.update_product_command_handler.handle_update_product_command = (
        update_product_func_mock
    )

    # Act
    handler.handler(minimal_event, lambda_context)

    # Assert
    update_product_func_mock.assert_called_once()
    command = update_product_func_mock.call_args.kwargs["command"]
    assertpy.assert_that(command.id).is_equal_to(id)
    assertpy.assert_that(command.description).is_equal_to(description)


def test_delete_product(lambda_context):
    # Arrange
    id = "test-id"

    minimal_event = api_gateway_proxy_event.APIGatewayProxyEvent(
        {
            "path": f"/products/{id}",
            "httpMethod": "DELETE",
            "requestContext": {  # correlation ID
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            },
        }
    )

    delete_product_func_mock = unittest.mock.create_autospec(
        spec=delete_product_command_handler.handle_delete_product_command
    )
    handler.delete_product_command_handler.handle_delete_product_command = (
        delete_product_func_mock
    )

    # Act
    handler.handler(minimal_event, lambda_context)

    # Assert
    delete_product_func_mock.assert_called_once()
    command = delete_product_func_mock.call_args.kwargs["command"]
    assertpy.assert_that(command.id).is_equal_to(id)


def test_get_product(lambda_context):
    # Arrange
    id = "test-id"
    minimal_event = api_gateway_proxy_event.APIGatewayProxyEvent(
        {
            "path": f"/products/{id}",
            "httpMethod": "GET",
            "requestContext": {  # correlation ID
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            },
        }
    )

    mock_query_service = unittest.mock.create_autospec(
        spec=products_query_service.ProductsQueryService
    )
    handler.products_query_service = mock_query_service

    # Act
    handler.handler(minimal_event, lambda_context)

    # Assert
    mock_query_service.get_product_by_id.assert_called_once()
    got_product_id = mock_query_service.get_product_by_id.call_args.kwargs["product_id"]
    assertpy.assert_that(got_product_id).is_equal_to(id)


def test_list_products(lambda_context):
    # Arrange
    page_size = 10
    minimal_event = api_gateway_proxy_event.APIGatewayProxyEvent(
        {
            "path": "/products",
            "httpMethod": "GET",
            "requestContext": {  # correlation ID
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            },
            "queryStringParameters": {"pageSize": str(page_size)},
        }
    )

    mock_query_service = unittest.mock.create_autospec(
        spec=products_query_service.ProductsQueryService
    )
    handler.products_query_service = mock_query_service

    # Act
    handler.handler(minimal_event, lambda_context)

    # Assert
    mock_query_service.list_products.assert_called_once()
    got_page_size = mock_query_service.list_products.call_args.kwargs["page_size"]
    assertpy.assert_that(got_page_size).is_equal_to(page_size)
