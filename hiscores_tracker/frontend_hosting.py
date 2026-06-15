import os

from aws_cdk import BundlingOptions, DockerImage, RemovalPolicy
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from constructs import Construct

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")


class FrontendHosting(Construct):
    """S3 + CloudFront hosting for the React frontend.

    Builds the Vite app inside a Docker container and uploads the output to a
    private S3 bucket served through a CloudFront distribution. A config.json
    is written alongside the static assets so the frontend can discover the
    API URL at runtime without it needing to be known at build time.
    """

    @property
    def url(self):
        return self._url

    def __init__(self, scope: Construct, id: str, *, query_api_url: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            self,
            "Bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
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
        )

        s3deploy.BucketDeployment(
            self,
            "Deploy",
            sources=[
                s3deploy.Source.asset(
                    _FRONTEND_DIR,
                    bundling=BundlingOptions(
                        image=DockerImage.from_registry("node:22-alpine"),
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

        self._url = f"https://{distribution.distribution_domain_name}"
