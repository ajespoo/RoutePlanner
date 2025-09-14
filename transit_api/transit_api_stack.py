from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Duration,
)


class TransitApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function for transit routing
        transit_lambda = _lambda.Function(
            self, "TransitFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("lambda"),
            handler="transit_handler.lambda_handler",
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "HSL_API_URL": "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1",
                "DIGITRANSIT_API_KEY": "DIGITRANSIT_API_KEY"
            }
        )

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