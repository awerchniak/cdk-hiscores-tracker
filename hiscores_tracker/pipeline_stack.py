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

    def __init__(
        self,
        scope: Construct,
        id: str,
        enabled: bool = True,
        stack_name: str = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        stack_kwargs = {"stack_name": stack_name} if stack_name is not None else {}
        stack = HiscoresTrackerStack(
            self, "HiscoresTrackerStack", enabled=enabled, **stack_kwargs
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
            "add-codepipeline",
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

        # Beta: event trigger disabled so it never polls the HiScores API on schedule.
        # Integration tests run here; passing them promotes to Prod.
        beta = HiscoresTrackerStage(self, "Beta", enabled=False)
        pipeline.add_stage(
            beta,
            post=[
                pipelines.ShellStep(
                    "IntegrationTest",
                    input=source,
                    env_from_cfn_outputs={
                        "TRIGGER_URL": beta.trigger_url,
                        "QUERY_URL": beta.query_url,
                    },
                    commands=[
                        "pip install requests",
                        "python run_integration_test.py -i $TRIGGER_URL -o $QUERY_URL",
                    ],
                )
            ],
        )

        # Prod: stack_name preserves the existing CloudFormation stack in-place.
        prod = HiscoresTrackerStage(
            self, "Prod", stack_name="HiscoresTrackerStack"
        )
        pipeline.add_stage(prod)
