import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import pipelines
from constructs import Construct

from .hiscores_tracker_stack import HiscoresTrackerStack


class HiscoresTrackerStage(cdk.Stage):
    @property
    def query_url(self):
        return self._query_url

    @property
    def trigger_url(self):
        return self._trigger_url

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        # stack_name keeps updates in-place against the pre-existing CloudFormation stack
        stack = HiscoresTrackerStack(
            self, "HiscoresTrackerStack", stack_name="HiscoresTrackerStack"
        )
        self._query_url = stack.query_url_output
        self._trigger_url = stack.trigger_url_output


class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        connection_arn = self.node.try_get_context("github_connection_arn")
        if not connection_arn:
            raise ValueError(
                "CDK context 'github_connection_arn' is required. "
                "Add it to cdk.json or pass -c github_connection_arn=<arn>."
            )

        source = pipelines.CodePipelineSource.connection(
            "awerchniak/cdk-hiscores-tracker",
            "main",
            connection_arn=connection_arn,
        )

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                commands=[
                    "npm install -g aws-cdk@2",
                    "pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
        )

        stage = HiscoresTrackerStage(self, "Deploy")
        pipeline.add_stage(
            stage,
            post=[
                pipelines.ShellStep(
                    "IntegrationTest",
                    input=source,
                    env_from_cfn_outputs={
                        "TRIGGER_URL": stage.trigger_url,
                        "QUERY_URL": stage.query_url,
                    },
                    commands=[
                        "pip install requests",
                        "python run_integration_test.py -i $TRIGGER_URL -o $QUERY_URL",
                    ],
                )
            ],
        )
