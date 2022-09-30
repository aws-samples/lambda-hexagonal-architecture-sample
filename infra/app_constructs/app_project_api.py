import constructs
from aws_cdk import RemovalPolicy, aws_apigateway, aws_lambda, aws_logs, aws_iam
import cdk_nag


class AppProjectApi(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        handler: aws_lambda.IFunction,
    ) -> None:
        super().__init__(scope, id)

        # Access logs group
        access_log_group = aws_logs.LogGroup(
            self,
            "SimpleCrudAppRestApiAccessLogGroup",
            log_group_name="simple-crud-api-access-log-group",
            removal_policy=RemovalPolicy.RETAIN,
            retention=aws_logs.RetentionDays.TWO_MONTHS,
        )

        # Stage options
        stage_options = aws_apigateway.StageOptions(
            stage_name="dev",
            access_log_destination=aws_apigateway.LogGroupLogDestination(
                access_log_group
            ),
            access_log_format=aws_apigateway.AccessLogFormat.json_with_standard_fields(
                caller=True,
                http_method=True,
                ip=True,
                protocol=True,
                request_time=True,
                resource_path=True,
                response_length=True,
                status=True,
                user=True,
            ),
            logging_level=aws_apigateway.MethodLoggingLevel.INFO,
            data_trace_enabled=True,
            metrics_enabled=True,
            tracing_enabled=True,
        )

        # Api Gateway
        self._api = aws_apigateway.LambdaRestApi(
            self,
            "SimpleCrudAppRestApi",
            handler=handler,
            proxy=False,
            description="Products API proxy to the Lambda",
            deploy_options=stage_options,
            rest_api_name="simple-crud-app-rest-api",
        )

        cw_role = [p for p in self._api.node.children if isinstance(p, aws_iam.Role)][0]
        cdk_nag.NagSuppressions.add_resource_suppressions(
            construct=cw_role,
            suppressions=[
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-IAM4",
                    reason="CloudWatch role is configured by CDK itself.",
                    applies_to=["Policy::arn:<AWS::Partition>:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"]
                ),
            ],
        )

        self._api.add_gateway_response(
            "client-error-response",
            type=aws_apigateway.ResponseType.DEFAULT_4_XX,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,\
                    X-Api-Key,x-amz-security-token'",
                "Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT,DELETE'",
            },
            templates={
                "application/json": '{ "message": $context.error.messageString }'
            },
        )

        self._api.add_gateway_response(
            "server-error-response",
            type=aws_apigateway.ResponseType.DEFAULT_5_XX,
            response_headers={
                "Access-Control-Allow-Origin": "'*'",
                "Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,\
                    X-Api-Key,x-amz-security-token'",
                "Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT,DELETE'",
            },
            templates={
                "application/json": '{ "message": $context.error.messageString }'
            },
        )

        aws_apigateway.RequestValidator(self, "api-gw-request-validator",
            rest_api=self._api,
        )

    @property
    def api(self) -> aws_apigateway.SpecRestApi:
        return self._api
