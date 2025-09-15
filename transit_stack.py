
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_logs as logs,
    CfnOutput
)
from constructs import Construct
import os

class TransitStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        lambda_function = _lambda.Function(
            self, "HelsinkiTransitFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_handler.lambda_handler",
            code=_lambda.Code.from_asset("."),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DIGITRANSIT_API_KEY": os.environ.get("DIGITRANSIT_API_KEY", ""),
                "SESSION_SECRET": os.environ.get("SESSION_SECRET", "cdk-default-secret")
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        # Create API Gateway
        api = apigateway.RestApi(
            self, "HelsinkiTransitApi",
            rest_api_name="Helsinki Transit Service",
            description="API for Helsinki transit route planning",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"]
            )
        )

        # Create API Gateway integration
        lambda_integration = apigateway.LambdaIntegration(lambda_function)

        # Add proxy resource to handle all requests
        api.root.add_proxy(
            default_integration=lambda_integration,
            any_method=True
        )

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="URL of the Helsinki Transit API"
        )

        # Output the Lambda function name
        CfnOutput(
            self, "LambdaFunctionName",
            value=lambda_function.function_name,
            description="Name of the Lambda function"
        )
