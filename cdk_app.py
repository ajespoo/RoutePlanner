#!/usr/bin/env python3

import os
import aws_cdk as cdk
from transit_stack import TransitStack

app = cdk.App()
TransitStack(app, "HelsinkiTransitStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'eu-north-1')
    )
)
app.synth()
