#!/usr/bin/env python3
import aws_cdk as cdk

from hiscores_tracker.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "HiscoresPipelineStack")

app.synth()
