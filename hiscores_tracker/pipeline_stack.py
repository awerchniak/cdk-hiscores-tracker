import aws_cdk as cdk
import boto3
import botocore.exceptions
from aws_cdk import Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from aws_cdk import pipelines
from constructs import Construct

from .hiscores_tracker_stack import HiscoresTrackerStack

_FRONTEND_DOMAIN_NAME_PARAM = "/hiscores-tracker/frontend-domain-name"

# ParameterNotFound: the deployer hasn't opted in to the feature.
# AccessDeniedException: the self-mutating pipeline's Synth step runs under
# its *current* CodeBuild role, which only gains permission to read a newly
# added parameter after a successful synth updates the pipeline itself (via
# the UpdatePipeline stage). So the first run after adding a new required
# permission sees AccessDenied rather than a clean "not found" -- treat it
# the same way so that run can still succeed and self-mutate; the parameter
# is then readable on the next run.
_MISSING_PARAM_ERROR_CODES = {"ParameterNotFound", "AccessDeniedException"}


def _try_get_ssm_parameter(name: str) -> str:
    """Resolve an SSM parameter at synth time, or None if it isn't available.

    Unlike ssm.StringParameter.value_from_lookup, this never fails synth when
    the parameter isn't readable -- used for opt-in features that must stay
    off by default.
    """
    try:
        return boto3.client("ssm").get_parameter(Name=name)["Parameter"]["Value"]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in _MISSING_PARAM_ERROR_CODES:
            return None
        raise


class HiscoresTrackerStage(cdk.Stage):
    @property
    def query_url(self):
        return self._query_url

    @property
    def trigger_url(self):
        return self._trigger_url

    @property
    def frontend_url(self):
        return self._frontend_url

    def __init__(
        self,
        scope: Construct,
        id: str,
        enabled: bool = True,
        stack_name: str = None,
        domain_name: str = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        stack_kwargs = {"stack_name": stack_name} if stack_name is not None else {}
        stack = HiscoresTrackerStack(
            self,
            "HiscoresTrackerStack",
            enabled=enabled,
            domain_name=domain_name,
            **stack_kwargs,
        )
        self._query_url = stack.query_url_output
        self._trigger_url = stack.trigger_url_output
        self._frontend_url = stack.frontend_url_output


class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        connection_arn = ssm.StringParameter.value_from_lookup(
            self, "/hiscores-tracker/github-connection-arn"
        )

        # Custom frontend domain is opt-in: only present if the deployer has
        # published their own domain via this SSM parameter. Absence is not
        # an error -- most deployers won't have set it.
        domain_name = _try_get_ssm_parameter(_FRONTEND_DOMAIN_NAME_PARAM)

        source = pipelines.CodePipelineSource.connection(
            "awerchniak/cdk-hiscores-tracker",
            "mainline",
            connection_arn=connection_arn,
        )

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            code_build_defaults=pipelines.CodeBuildOptions(
                partial_build_spec=codebuild.BuildSpec.from_object(
                    {"phases": {"install": {"commands": ["n 22"]}}}
                ),
                role_policy=[
                    iam.PolicyStatement(
                        actions=["ssm:GetParameter", "ssm:GetParameters"],
                        resources=[
                            f"arn:aws:ssm:{self.region}:{self.account}"
                            ":parameter/hiscores-tracker/github-connection-arn",
                            f"arn:aws:ssm:{self.region}:{self.account}"
                            f":parameter{_FRONTEND_DOMAIN_NAME_PARAM}",
                        ],
                    ),
                    iam.PolicyStatement(
                        # Needed for route53.HostedZone.from_lookup during
                        # synth when a custom frontend domain is configured.
                        actions=[
                            "route53:GetHostedZone",
                            "route53:ListHostedZonesByName",
                        ],
                        resources=["*"],
                    ),
                ],
            ),
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                commands=[
                    "npm install -g aws-cdk",
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
        # domain_name is only ever set here, never on Beta -- CloudFront
        # requires alias hostnames to be unique across all distributions in
        # the account, so Beta and Prod can't both claim the same domain.
        # route53.HostedZone.from_lookup (used when domain_name is set) needs
        # a concrete account/region at synth time, so only pin one down when
        # the feature is actually in use.
        prod = HiscoresTrackerStage(
            self,
            "Prod",
            stack_name="HiscoresTrackerStack",
            domain_name=domain_name,
            env=(
                cdk.Environment(account=self.account, region=self.region)
                if domain_name is not None
                else None
            ),
        )
        pipeline.add_stage(prod)
