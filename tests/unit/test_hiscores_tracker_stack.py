import aws_cdk as core
import aws_cdk.assertions as assertions
import botocore.exceptions
import pytest

from hiscores_tracker.hiscores_tracker_stack import HiscoresTrackerStack
from hiscores_tracker.pipeline_stack import (
    HiscoresTrackerStage,
    PipelineStack,
    _try_get_ssm_parameter,
)


def test_synthesize():
    app = core.App()
    stack = HiscoresTrackerStack(app, "hiscores-logger")
    template = assertions.Template.from_stack(stack)

    assert stack.query_url is not None
    assert stack.trigger_url is not None
    assert stack.frontend_url is not None
    assert stack.query_url_output is not None
    assert stack.trigger_url_output is not None
    assert stack.frontend_url_output is not None

    # Assert no extraneous resources
    # 4 application Lambdas + 1 BucketDeployment handler + 1 auto-delete handler
    template.resource_count_is("AWS::Lambda::Function", 6)
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


def test_synthesize_with_custom_domain():
    app = core.App()
    stack = HiscoresTrackerStack(
        app,
        "hiscores-logger-custom-domain",
        domain_name="example.com",
        env=core.Environment(account="123456789012", region="us-east-1"),
    )
    template = assertions.Template.from_stack(stack)

    assert stack.frontend_url == "https://example.com"

    template.resource_count_is("AWS::CertificateManager::Certificate", 1)
    template.has_resource_properties(
        "AWS::CertificateManager::Certificate",
        {"DomainName": "example.com", "ValidationMethod": "DNS"},
    )
    template.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": assertions.Match.object_like(
                {
                    "Aliases": ["example.com"],
                    "ViewerCertificate": assertions.Match.object_like(
                        {"SslSupportMethod": "sni-only"}
                    ),
                }
            )
        },
    )
    # Alias A + AAAA records; no separate record for cert validation since
    # AWS::CertificateManager::Certificate handles that natively when given
    # a HostedZoneId.
    template.resource_count_is("AWS::Route53::RecordSet", 2)


def test_try_get_ssm_parameter_returns_value(mocker):
    mock_client = mocker.Mock()
    mock_client.get_parameter.return_value = {"Parameter": {"Value": "example.com"}}
    mocker.patch(
        "hiscores_tracker.pipeline_stack.boto3.client", return_value=mock_client
    )

    assert _try_get_ssm_parameter("/some/param") == "example.com"


def test_try_get_ssm_parameter_returns_none_when_missing(mocker):
    mock_client = mocker.Mock()
    mock_client.get_parameter.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ParameterNotFound", "Message": "not found"}},
        "GetParameter",
    )
    mocker.patch(
        "hiscores_tracker.pipeline_stack.boto3.client", return_value=mock_client
    )

    assert _try_get_ssm_parameter("/some/param") is None


def test_try_get_ssm_parameter_returns_none_when_access_denied(mocker):
    # Self-mutating pipelines run Synth under the *current* CodeBuild role,
    # which only gains permission to read a newly added parameter after a
    # successful synth updates the pipeline itself. The first run after
    # adding a new required permission sees AccessDenied rather than a clean
    # "not found" -- this must be treated the same way so that run can still
    # succeed and self-mutate.
    mock_client = mocker.Mock()
    mock_client.get_parameter.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "not authorized"}},
        "GetParameter",
    )
    mocker.patch(
        "hiscores_tracker.pipeline_stack.boto3.client", return_value=mock_client
    )

    assert _try_get_ssm_parameter("/some/param") is None


def test_try_get_ssm_parameter_reraises_other_errors(mocker):
    mock_client = mocker.Mock()
    mock_client.get_parameter.side_effect = botocore.exceptions.ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "nope"}},
        "GetParameter",
    )
    mocker.patch(
        "hiscores_tracker.pipeline_stack.boto3.client", return_value=mock_client
    )

    with pytest.raises(botocore.exceptions.ClientError):
        _try_get_ssm_parameter("/some/param")


def test_synthesize_pipeline_stack(mocker):
    mocker.patch(
        "hiscores_tracker.pipeline_stack._try_get_ssm_parameter", return_value=None
    )
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
    assert stage.frontend_url is not None

    stage_with_name = HiscoresTrackerStage(app, "TestStageNamed", stack_name="MyStack")
    assert stage_with_name.query_url is not None
    assert stage_with_name.trigger_url is not None
    assert stage_with_name.frontend_url is not None
