import json
import os
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR

from aws_lambda_powertools import logging
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

logger = logging.Logger(level=os.environ.get("LOG_LEVEL", "INFO"))


@lambda_handler_decorator
def handle_exceptions(handler, event, context, user_exceptions, cors_config):
    try:
        return handler(event, context)
    except Exception as e:
        if isinstance(e, tuple(user_exceptions)):
            logger.exception("User exception.")
            return {
                "statusCode": BAD_REQUEST,
                "headers": cors_config.to_dict(),
                "body": json.dumps({"message": str(e)}),
                "isBase64Encoded": False,
            }
        else:
            logger.exception("Unhandled exception.")
            return {
                "statusCode": INTERNAL_SERVER_ERROR,
                "headers": cors_config.to_dict(),
                "body": json.dumps({"message": "Internal server error."}),
                "isBase64Encoded": False,
            }
