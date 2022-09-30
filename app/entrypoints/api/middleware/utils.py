from functools import wraps
from typing import Type

from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.parser.types import Model


def parse_event(model: Type[Model], app_context):
    def real_decorator(function):
        @wraps(function)
        def wrapper(**kwargs):
            event = parse(event=app_context.current_event.json_body, model=model)
            return function(event, **kwargs)

        return wrapper

    return real_decorator
