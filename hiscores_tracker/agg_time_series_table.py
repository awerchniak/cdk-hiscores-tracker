from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as ddb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_lambda_event_sources as lambda_event_sources
from constructs import Construct

from .util import package_lambda


class AggregatingTimeSeriesTable(Construct):
    """DynamoDB timeseries table with automatic aggregation.

    In the future, if this sort of thing is useful, we can make it
    much more agnostic. For example, right now the structure of
    the database is mostly hard-coded to the `player,timestamp`
    key structure and HiScores-related attribute schema.
    Aggregation strategy is hard-coded. etc. For now, it's nice to
    have this functionality at least separated into a logical block.

    """

    @property
    def table(self):
        return self._table

    @property
    def query_api(self):
        return self._query_api

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Provision Dynamo Table: provisioned capacity, streaming enabled
        self._table = ddb.Table(
            self,
            "HiScores",
            partition_key=ddb.Attribute(name="player", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="timestamp", type=ddb.AttributeType.STRING),
            encryption=ddb.TableEncryption.AWS_MANAGED,
            read_capacity=20,
            write_capacity=5,
            removal_policy=RemovalPolicy.DESTROY,
            stream=ddb.StreamViewType.NEW_IMAGE,
        )

        # Provision aggregator Lambda and grant write access
        aggregator = package_lambda(
            scope=self,
            handler_name="aggregator",
            function_name="DailyAggregatorLambda",
            description="Aggregate write events into daily rows.",
            environment={
                "HISCORES_TABLE_NAME": self._table.table_name,
            },
            retry_attempts=0,
        )
        self._table.grant_read_write_data(aggregator)

        # Subscribe aggregator to table events
        aggregator.add_event_source(
            lambda_event_sources.DynamoEventSource(
                self._table,
                starting_position=_lambda.StartingPosition.TRIM_HORIZON,
                batch_size=1,
                retry_attempts=0,
            )
        )

        # Provision queryer Lambda and grant read access
        queryer = package_lambda(
            scope=self,
            handler_name="read_hiscores_table",
            function_name="QueryHiScoresLambda",
            description="Retrieve data from HiScoresTable for a given player.",
            environment={
                "HISCORES_TABLE_NAME": self._table.table_name,
            },
            timeout=Duration.seconds(60),
        )
        self._table.grant_read_data(queryer)

        # Expose Rest API for queryer
        self._query_api = apigw.LambdaRestApi(
            self,
            "QueryHiScoresData",
            handler=queryer,
            parameters={"player": "str", "startTime": "str", "endTime": "str"},
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET", "OPTIONS"],
            ),
        )
        self._query_api.root.add_method("GET")
