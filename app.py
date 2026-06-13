#!/usr/bin/env python3
import os

import aws_cdk as cdk

from hiscores_tracker.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(
    app,
    "HiscoresPipelineStack",
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)

app.synth()
