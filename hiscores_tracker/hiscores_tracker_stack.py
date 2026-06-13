from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_apigateway as apigw
from constructs import Construct

from .agg_time_series_table import AggregatingTimeSeriesTable
from .hiscores_logger import HiScoresLogger


class HiscoresTrackerStack(Stack):
    """Track your OldSchoolRuneScape HiScores metrics over time."""

    @property
    def query_url(self):
        return self._query_url

    @property
    def trigger_url(self):
        return self._trigger_url

    @property
    def query_url_output(self):
        return self._query_url_output

    @property
    def trigger_url_output(self):
        return self._trigger_url_output

    def __init__(self, scope: Construct, construct_id: str, enabled: bool = True, **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # Provision HiScores AggregatingTimeSeriesTable
        atst = AggregatingTimeSeriesTable(self, "HiScoresATST")
        self._query_url = atst.query_api.url

        # Provision HiScores API Logger
        hiscores_logger = HiScoresLogger(self, "OSRSHiScoresLogger", table=atst.table, enabled=enabled)

        # Expose Rest API to trigger orchestrator
        trigger_api = apigw.LambdaRestApi(
            self,
            "TriggerHiScoresLogEvent",
            handler=hiscores_logger.orchestrator,
        )
        trigger_api.root.add_method("POST")
        self._trigger_url = trigger_api.url

        self._query_url_output = CfnOutput(self, "QueryUrl", value=self._query_url)
        self._trigger_url_output = CfnOutput(self, "TriggerUrl", value=self._trigger_url)
