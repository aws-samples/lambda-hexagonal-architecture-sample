import unittest
import uuid

import assertpy

from app.domain.command_handlers import (
    create_product_command_handler,
    delete_product_command_handler,
    update_product_command_handler,
)
from app.domain.commands import (
    create_product_command,
    delete_product_command,
    update_product_command,
)
from app.domain.ports import unit_of_work


def test_create_product_should_store_in_repository():
    # Arrange
    mock_unit_of_work = unittest.mock.create_autospec(
        spec=unit_of_work.UnitOfWork, instance=True
    )
    mock_unit_of_work.products = unittest.mock.create_autospec(
        spec=unit_of_work.ProductsRepository, instance=True
    )

    command = create_product_command.CreateProductCommand(
        name="Test Product",
        description="Test Description",
    )

    # Act
    create_product_command_handler.handle_create_product_command(
        command=command, unit_of_work=mock_unit_of_work
    )

    # Assert
    mock_unit_of_work.commit.assert_called_once()
    product = mock_unit_of_work.products.add.call_args.args[0]

    assertpy.assert_that(product.name).is_equal_to("Test Product")
    assertpy.assert_that(product.description).is_equal_to("Test Description")


def test_update_product_should_only_update_specified_property():
    # Arrange
    mock_unit_of_work = unittest.mock.create_autospec(
        spec=unit_of_work.UnitOfWork, instance=True
    )
    mock_unit_of_work.products = unittest.mock.create_autospec(
        spec=unit_of_work.ProductsRepository, instance=True
    )

    # Update only the description
    product_id = str(uuid.uuid4())
    new_description = "New Description"
    command = update_product_command.UpdateProductCommand(
        id=product_id, description=new_description
    )

    # Act
    update_product_command_handler.handle_update_product_command(
        command=command, unit_of_work=mock_unit_of_work
    )

    # Assert
    mock_unit_of_work.commit.assert_called_once()
    updated_attributes = mock_unit_of_work.products.update_attributes.call_args.kwargs

    assertpy.assert_that(updated_attributes["product_id"]).is_equal_to(product_id)
    assertpy.assert_that(updated_attributes["description"]).is_equal_to(new_description)


def test_delete_product_should_delete_from_repository():
    # Arrange
    mock_unit_of_work = unittest.mock.create_autospec(
        spec=unit_of_work.UnitOfWork, instance=True
    )
    mock_unit_of_work.products = unittest.mock.create_autospec(
        spec=unit_of_work.ProductsRepository, instance=True
    )

    product_id = str(uuid.uuid4())
    command = delete_product_command.DeleteProductCommand(id=product_id)

    # Act
    delete_product_command_handler.handle_delete_product_command(
        command=command, unit_of_work=mock_unit_of_work
    )

    # Assert
    mock_unit_of_work.commit.assert_called_once()
    deleted_product_id = mock_unit_of_work.products.delete.call_args.kwargs[
        "product_id"
    ]

    assertpy.assert_that(deleted_product_id).is_equal_to(product_id)
