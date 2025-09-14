from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
    aws_ssm as ssm,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction


class TransitApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SSM parameter for API key (would be set manually or via CI/CD)
        api_key_param = ssm.StringParameter(
            self, "DigitransitApiKey",
            parameter_name="/transit-api/digitransit-api-key",
            string_value="PLACEHOLDER_SET_MANUALLY",
            description="Digitransit API key for HSL route planning"
        )

        # Lambda function for transit routing with proper Python bundling
        transit_lambda = PythonFunction(
            self, "TransitFunction",
            entry="lambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler",
            index="transit_handler.py",
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "HSL_API_URL": "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1",
                "DIGITRANSIT_API_KEY_PARAM": api_key_param.parameter_name
            }
        )

        # Grant permission to read the API key parameter
        api_key_param.grant_read(transit_lambda)

        # REST API Gateway
        api = apigateway.RestApi(
            self, "TransitApi",
            rest_api_name="Transit Route API",
            description="REST API for Helsinki transit route planning",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )

        # Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            transit_lambda,
            proxy=True,
            allow_test_invoke=True
        )

        # Add routes resource
        routes_resource = api.root.add_resource("routes")
        routes_resource.add_method("GET", lambda_integration)