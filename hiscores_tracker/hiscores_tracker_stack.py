import aws_cdk as cdk
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_apigateway as apigw
from constructs import Construct

from .agg_time_series_table import AggregatingTimeSeriesTable
from .frontend_hosting import FrontendHosting
from .hiscores_logger import HiScoresLogger


class HiscoresTrackerStack(Stack):
    """Track your OldSchoolRuneScape HiScores metrics over time."""

    @property
    def query_url(self) -> str:
        return self._query_url

    @property
    def trigger_url(self) -> str:
        return self._trigger_url

    @property
    def frontend_url(self) -> str:
        return self._frontend_url

    @property
    def query_url_output(self) -> CfnOutput:
        return self._query_url_output

    @property
    def trigger_url_output(self) -> CfnOutput:
        return self._trigger_url_output

    @property
    def frontend_url_output(self) -> CfnOutput:
        return self._frontend_url_output

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        enabled: bool = True,
        domain_name: str | None = None,
        stack_name: str | None = None,
        env: cdk.Environment | None = None,
    ) -> None:

        super().__init__(scope, construct_id, stack_name=stack_name, env=env)

        # Provision HiScores AggregatingTimeSeriesTable
        atst = AggregatingTimeSeriesTable(self, "HiScoresATST")
        self._query_url = atst.query_api.url

        # Provision HiScores API Logger
        hiscores_logger = HiScoresLogger(
            self, "OSRSHiScoresLogger", table=atst.table, enabled=enabled
        )

        # Expose Rest API to trigger orchestrator
        trigger_api = apigw.LambdaRestApi(
            self,
            "TriggerHiScoresLogEvent",
            handler=hiscores_logger.orchestrator,
        )
        trigger_api.root.add_method("POST")
        self._trigger_url = trigger_api.url

        # Host the React frontend on S3 + CloudFront
        frontend = FrontendHosting(
            self,
            "Frontend",
            query_api_url=self._query_url,
            domain_name=domain_name,
        )
        self._frontend_url = frontend.url

        self._query_url_output = CfnOutput(self, "QueryUrl", value=self._query_url)
        self._trigger_url_output = CfnOutput(
            self, "TriggerUrl", value=self._trigger_url
        )
        self._frontend_url_output = CfnOutput(
            self, "FrontendUrl", value=self._frontend_url
        )
