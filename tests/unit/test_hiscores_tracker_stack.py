import aws_cdk as core
import aws_cdk.assertions as assertions

from hiscores_tracker.hiscores_tracker_stack import HiscoresTrackerStack
from hiscores_tracker.pipeline_stack import HiscoresTrackerStage, PipelineStack


def test_synthesize():
    app = core.App()
    stack = HiscoresTrackerStack(app, "hiscores-logger")
    template = assertions.Template.from_stack(stack)

    assert stack.query_url is not None
    assert stack.trigger_url is not None
    assert stack.query_url_output is not None
    assert stack.trigger_url_output is not None

    # Assert no extraneous resources
    template.resource_count_is("AWS::Lambda::Function", 4)
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    template.resource_count_is("AWS::SQS::Queue", 1)
    template.resource_count_is("AWS::ApiGateway::RestApi", 2)
    template.resource_count_is("AWS::Events::Rule", 1)

    # Test HiScoresTable created
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [
                {"AttributeName": "player", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "player", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            "ProvisionedThroughput": {"ReadCapacityUnits": 20, "WriteCapacityUnits": 5},
            "SSESpecification": {"SSEEnabled": True},
            "StreamSpecification": {"StreamViewType": "NEW_IMAGE"},
        },
    )

    # Test Orchestrator created
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "orchestrator.handler.handler",
            "Runtime": "python3.13",
        },
    )

    # Test GetAndParse created
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "get_and_parse_hiscores.handler.handler",
            "Runtime": "python3.13",
        },
    )

    # Test Aggregator created
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "aggregator.handler.handler",
            "Runtime": "python3.13",
        },
    )

    # Test Queryer created
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Handler": "read_hiscores_table.handler.handler",
            "Runtime": "python3.13",
        },
    )


def test_synthesize_pipeline_stack():
    app = core.App()
    stack = PipelineStack(
        app,
        "pipeline",
        env=core.Environment(account="123456789012", region="us-east-1"),
    )
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::CodePipeline::Pipeline", 1)
    template.has_resource_properties(
        "AWS::CodePipeline::Pipeline",
        {
            "Stages": assertions.Match.array_with(
                [
                    assertions.Match.object_like({"Name": "Source"}),
                    assertions.Match.object_like({"Name": "Build"}),
                    assertions.Match.object_like({"Name": "Beta"}),
                    assertions.Match.object_like({"Name": "Prod"}),
                ]
            )
        },
    )


def test_hiscores_tracker_stage_properties():
    app = core.App()
    stage = HiscoresTrackerStage(app, "TestStage")
    assert stage.query_url is not None
    assert stage.trigger_url is not None

    stage_with_name = HiscoresTrackerStage(app, "TestStageNamed", stack_name="MyStack")
    assert stage_with_name.query_url is not None
    assert stage_with_name.trigger_url is not None
