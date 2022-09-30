from typing import List, Optional

from aws_cdk import aws_lambda, aws_lambda_python_alpha
from constructs import Construct


class SharedLayer(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        compatible_runtimes: List[aws_lambda.Runtime],
        entry: str,
        layer_version_name: str,
        extra_bundling_options: Optional[
            aws_lambda_python_alpha.BundlingOptions
        ] = None,
    ) -> None:

        super().__init__(scope, construct_id)

        self._libraries_layer = aws_lambda_python_alpha.PythonLayerVersion(
            scope,
            "SimpleCrudAppLayers",
            layer_version_name=layer_version_name,
            entry=entry,
            compatible_runtimes=compatible_runtimes,
            bundling=extra_bundling_options,
        )

    @property
    def libraries_layer(self):
        return self._libraries_layer
