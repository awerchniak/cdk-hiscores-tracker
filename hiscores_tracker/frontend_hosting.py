import os

from aws_cdk import BundlingOptions, DockerImage, RemovalPolicy
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from constructs import Construct

_FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "frontend"
)


class FrontendHosting(Construct):
    """S3 + CloudFront hosting for the React frontend.

    Builds the Vite app inside a Docker container and uploads the output to a
    private S3 bucket served through a CloudFront distribution. A config.json
    is written alongside the static assets so the frontend can discover the
    API URL at runtime without it needing to be known at build time.
    """

    @property
    def url(self) -> str:
        return self._url

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        query_api_url: str,
        domain_name: str | None = None,
    ) -> None:
        super().__init__(scope, id)

        bucket = s3.Bucket(
            self,
            "Bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Custom domain is opt-in: only set up if the deployer has published
        # their own domain via the /hiscores-tracker/frontend-domain-name SSM
        # parameter. Everyone else gets the plain *.cloudfront.net domain.
        certificate: acm.ICertificate | None = None
        hosted_zone: route53.IHostedZone | None = None
        if domain_name is not None:
            hosted_zone = route53.HostedZone.from_lookup(
                self, "Zone", domain_name=domain_name
            )
            certificate = acm.Certificate(
                self,
                "Certificate",
                domain_name=domain_name,
                validation=acm.CertificateValidation.from_dns(hosted_zone),
            )

        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=(
                    cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
                ),
            ),
            default_root_object="index.html",
            # Route unknown paths back to index.html for SPA client-side routing
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
            domain_names=[domain_name] if domain_name is not None else None,
            certificate=certificate,
        )

        if domain_name is not None:
            assert hosted_zone is not None
            alias_target = route53.RecordTarget.from_alias(
                route53_targets.CloudFrontTarget(distribution)
            )
            route53.ARecord(
                self,
                "AliasRecord",
                zone=hosted_zone,
                record_name=domain_name,
                target=alias_target,
            )
            route53.AaaaRecord(
                self,
                "AliasRecordIPv6",
                zone=hosted_zone,
                record_name=domain_name,
                target=alias_target,
            )

        s3deploy.BucketDeployment(
            self,
            "Deploy",
            sources=[
                s3deploy.Source.asset(
                    _FRONTEND_DIR,
                    bundling=BundlingOptions(
                        # ECR Public mirror, not Docker Hub directly -- avoids
                        # Docker Hub's anonymous pull rate limit, which the
                        # shared CodeBuild NAT IP hits under repeated builds.
                        image=DockerImage.from_registry(
                            "public.ecr.aws/docker/library/node:22-alpine"
                        ),
                        command=[
                            "sh",
                            "-c",
                            "npm ci && npm run build && cp -r dist/* /asset-output/",
                        ],
                    ),
                ),
                # Written after the build so the frontend can discover the API
                # URL at runtime rather than needing it baked in at build time.
                s3deploy.Source.json_data("config.json", {"apiUrl": query_api_url}),
            ],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        self._url = (
            f"https://{domain_name}"
            if domain_name is not None
            else f"https://{distribution.distribution_domain_name}"
        )
