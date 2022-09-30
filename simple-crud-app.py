#!/usr/bin/env python3
import aws_cdk
import cdk_nag
from infra import simple_crud_app_stack

app = aws_cdk.App()
simple_crud_app_stack.SimpleCrudAppStack(
    app, "SimpleCrudAppStack", stack_name="simple-crud-app"
)

aws_cdk.Aspects.of(app).add(cdk_nag.AwsSolutionsChecks(reports=True, verbose=True))

app.synth()
