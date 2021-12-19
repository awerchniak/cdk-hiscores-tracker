from constructs import Construct
from aws_cdk import (
    aws_dynamodb as ddb,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    Duration,
)

import os
import subprocess
from tempfile import TemporaryDirectory

from hiscores_tracker.util import package_lambda


class HiScoresLogger(Construct):
    """Automatically log OldSchoolRuneScape HiScores metrics to Dynamo table."""

    def __init__(
        self, scope: Construct, id: str, table: ddb.ITable, enabled=True, **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        # Provision GetAndParseHiScores Lambda
        handler_name = "get_and_parse_hiscores"
        with TemporaryDirectory() as layer_output_dir:
            get_and_parse_handler = package_lambda(
                scope=self,
                handler_name="get_and_parse_hiscores",
                function_name="GetAndParseHiScoresLambda",
                description="Retrieve, parse, and save HiScores data for a given player.",
                environment={
                    "HISCORES_TABLE_NAME": table.table_name,
                },
                layers=[
                    self.create_dependencies_layer(
                        layer_id="get-and-parse-dependencies",
                        requirements_file=os.path.join(
                            "lambda", handler_name, "requirements.txt"
                        ),
                        output_dir=layer_output_dir,
                    )
                ],
            )
        table.grant_write_data(get_and_parse_handler)

        # Provision GetAndParseForPlayer Queue
        get_and_parse_queue = sqs.Queue(
            self, "GetAndParseForPlayerQueue", retention_period=Duration.days(1)
        )
        get_and_parse_handler.add_event_source(
            lambda_event_sources.SqsEventSource(get_and_parse_queue, batch_size=1)
        )

        # Create Orchestrator Lambda
        handler_name = "orchestrator"
        orchestrator_handler = package_lambda(
            scope=self,
            handler_name="orchestrator",
            function_name="OrchestratorLambda",
            description="Read configuration and kick off HiScores tracking.",
            environment={"GET_AND_PARSE_QUEUE_URL": get_and_parse_queue.queue_url},
        )
        get_and_parse_queue.grant_send_messages(orchestrator_handler)

        # Create Event to trigger Orchestrator on schedule
        rule = events.Rule(
            self,
            "OrchestratorTrigger",
            description="Trigger Orchestrator Lambda.",
            enabled=enabled,
            schedule=events.Schedule.cron(
                minute="*/30",  # Trigger every 30 minutes
                hour="0-2,7-23",  # Trigger between 7am and 2am
            ),
        )
        rule.add_target(targets.LambdaFunction(orchestrator_handler))

    def create_dependencies_layer(
        self, layer_id: str, requirements_file: str, output_dir: str
    ) -> _lambda.LayerVersion:
        """Create LambdaLayer with required dependencies.

        Citation: https://github.com/esteban-uo/aws-cdk-python-application-dependencies
        """

        subprocess.check_call(
            f"pip install -r {requirements_file} -t {output_dir}/python".split()
        )
        layer_code = _lambda.Code.from_asset(output_dir)
        return _lambda.LayerVersion(self, layer_id, code=layer_code)
