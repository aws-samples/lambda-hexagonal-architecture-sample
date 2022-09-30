from app.domain.commands import delete_product_command
from app.domain.ports import unit_of_work


def handle_delete_product_command(
    command: delete_product_command.DeleteProductCommand,
    unit_of_work: unit_of_work.UnitOfWork,
) -> str:

    with unit_of_work:
        unit_of_work.products.delete(product_id=command.id)
        unit_of_work.commit()

    return command.id
