import os
import shutil
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from aws_cdk import aws_lambda as _lambda


@contextmanager
def wraps_code_dir(code_dir):
    """Copy a code directory into a temporary directory."""
    with TemporaryDirectory() as tmp_dir:
        new_path = os.path.join(tmp_dir, os.path.basename(code_dir))
        shutil.copytree(code_dir, new_path)
        yield tmp_dir


def package_lambda(
    scope,
    handler_name,
    function_name,
    description,
    environment=None,
    layers=None,
    retry_attempts=None,
    timeout=None,
):
    """Package handler source and provision Lambda function."""
    original_code_dir = os.path.join("lambda", handler_name)
    with wraps_code_dir(code_dir=original_code_dir) as code_dir:
        return _lambda.Function(
            scope,
            function_name,
            description=description,
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset(code_dir),
            handler=f"{handler_name}.handler.handler",
            environment=environment,
            layers=layers,
            retry_attempts=retry_attempts,
            timeout=timeout,
        )
