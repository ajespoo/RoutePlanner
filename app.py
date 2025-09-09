#!/usr/bin/env python3
import aws_cdk as cdk
from transit_api.transit_api_stack import TransitApiStack

app = cdk.App()
TransitApiStack(app, "TransitApiStack")
app.synth()