import uuid
from datetime import datetime, timezone

from app.domain.commands import create_product_command
from app.domain.model import product
from app.domain.ports import unit_of_work


def handle_create_product_command(
    command: create_product_command.CreateProductCommand,
    unit_of_work: unit_of_work.UnitOfWork,
) -> str:
    current_time = datetime.now(timezone.utc).isoformat()
    id = str(uuid.uuid4())

    product_obj = product.Product(
        id=id,
        name=command.name,
        description=command.description,
        createDate=current_time,
        lastUpdateDate=current_time,
    )

    with unit_of_work:
        unit_of_work.products.add(product_obj)
        unit_of_work.commit()

    return id
