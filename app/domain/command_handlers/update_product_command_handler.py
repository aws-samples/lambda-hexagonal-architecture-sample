from datetime import datetime, timezone

from app.domain.commands import update_product_command
from app.domain.ports import unit_of_work


def handle_update_product_command(
    command: update_product_command.UpdateProductCommand,
    unit_of_work: unit_of_work.UnitOfWork,
) -> str:
    current_time = datetime.now(timezone.utc).isoformat()

    attr_to_update = {
        "lastUpdateDate": current_time,
    }
    if command.name:
        attr_to_update["name"] = command.name
    if command.description:
        attr_to_update["description"] = command.description

    with unit_of_work:
        unit_of_work.products.update_attributes(product_id=command.id, **attr_to_update)
        unit_of_work.commit()

    return command.id
