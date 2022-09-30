import aws_cdk
import constructs
from aws_cdk import aws_apigateway, aws_dynamodb, aws_lambda
import cdk_nag
from infra.app_constructs import app_project, app_project_api, layers


class SimpleCrudAppStack(aws_cdk.Stack):
    def __init__(
        self, scope: constructs.Construct, construct_id: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        table = aws_dynamodb.Table(
            self,
            "simple-crud-app-table",
            partition_key=aws_dynamodb.Attribute(
                name="PK", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="SK", type=aws_dynamodb.AttributeType.STRING
            ),
            table_name="simple-crud-app-table",
        )

        runtime = aws_lambda.Runtime.PYTHON_3_9
        self._layer = layers.SharedLayer(
            self,
            "SharedLayer",
            compatible_runtimes=[runtime],
            layer_version_name="simple_crud_app_libraries",
            entry="app/libraries",
        )

        api_entrypoint_name = "simple-crud-api"

        self._app_project = app_project.AppProject(
            self,
            "SimpleCrudAppProject",
            app_entry_points=[
                app_project.AppEntryPoint(
                    name=api_entrypoint_name,
                    root="app",
                    entry="app/entrypoints/api",
                    environment={"TABLE_NAME": table.table_name},
                    permissions=[
                        lambda lambda_f: table.grant_read_write_data(lambda_f)
                    ],
                )
            ],
            app_layers=[self._layer.libraries_layer],
            runtime=runtime,
        )

        # API Gateway
        self._api = app_project_api.AppProjectApi(
            self,
            "SimpleCrudAppApi",
            self._app_project.app_entries[api_entrypoint_name],
        )

        products = self._api.api.root.add_resource("products")
        products.add_method(
            "GET", authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        products.add_method(
            "POST", authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        products_id = products.add_resource("{id}")
        products_id.add_method(
            "GET", authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        products_id.add_method(
            "PUT", authorization_type=aws_apigateway.AuthorizationType.IAM
        )
        products_id.add_method(
            "DELETE", authorization_type=aws_apigateway.AuthorizationType.IAM
        )

        products.add_cors_preflight(allow_origins=["*"], allow_methods=["GET", "POST"])
        products_id.add_cors_preflight(
            allow_origins=["*"], allow_methods=["GET", "PUT", "DELETE"]
        )

        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(
            stack=self,
            path='/SimpleCrudAppStack/SimpleCrudAppApi/SimpleCrudAppRestApi/Default/products/OPTIONS/Resource',
            suppressions=[
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-APIG4",
                    reason="OPTIONS methods have no authorization.",
                ),
            ],
        )
        cdk_nag.NagSuppressions.add_resource_suppressions_by_path(
            stack=self,
            path='/SimpleCrudAppStack/SimpleCrudAppApi/SimpleCrudAppRestApi/Default/products/{id}/OPTIONS/Resource',
            suppressions=[
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-APIG4",
                    reason="OPTIONS methods have no authorization.",
                ),
            ],
        )

        cdk_nag.NagSuppressions.add_resource_suppressions(
            construct=self._api,
            apply_to_children=True,
            suppressions=[
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-COG4",
                    reason="API methods use IAM authorization instead of Cognito.",
                ),
            ],
        )