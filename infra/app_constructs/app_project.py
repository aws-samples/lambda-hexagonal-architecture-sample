from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Sequence

import aws_cdk.aws_iam as aws_iam
import aws_cdk.aws_lambda as aws_lambda
import constructs

from infra.app_constructs import app_project_function


@dataclass
class AppLibrary:
    name: str
    entry: str


@dataclass
class AppEntryPoint:
    name: str
    entry: str
    root: str
    environment: Optional[Mapping[str, str]]
    permissions: Sequence[Callable[[aws_iam.IGrantable], aws_iam.Grant]]


class AppProject(constructs.Construct):
    def __init__(
        self,
        scope: constructs.Construct,
        id: str,
        runtime: aws_lambda.Runtime,
        app_layers: Sequence[aws_lambda.ILayerVersion],
        app_entry_points: Sequence[AppEntryPoint],
    ) -> None:
        super().__init__(scope, id)

        self._app_entry_functions: dict[str, aws_lambda.Function] = {
            app.name: app_project_function.AppProjectFunction(
                self,
                app.name,
                function_name=app.name,
                entry=app.entry,
                root=app.root,
                runtime=runtime,
                layers=app_layers,
                environment=app.environment,
                permissions=app.permissions or [],
            ).function
            for app in app_entry_points
        }

    @property
    def app_entries(self) -> dict[str, aws_lambda.Function]:
        return self._app_entry_functions
