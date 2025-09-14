# Transit API Deployment Guide

## Overview
This REST API provides Helsinki transit route planning specifically designed for Andrea's daily commute from Aalto University to KONE Building in Keilaniemi. The API uses HSL's Digitransit GraphQL service and can be deployed to AWS using CDK.

## Features
- REST API that accepts arrival time and stop names
- Returns detailed route information including departure times, modes of transport, and transfers
- Proper arrival time constraint (tells you when to leave for a specific arrival time)
- Secure API key management via AWS SSM Parameter Store
- Ready for AWS Lambda deployment with CDK

## API Endpoints

### GET /routes
Returns transit routes for specified arrival time and stops.

**Query Parameters:**
- `arrival_time` (required): Format `yyyyMMddHHmmss` (e.g., `20250916084500` for Sep 16, 2025 at 08:45:00)
- `from_stop` (optional): Departure stop name (default: "Aalto Yliopisto")
- `to_stop` (optional): Destination stop name (default: "Keilaniemi")

**Example:**
```
GET /routes?arrival_time=20250916084500&from_stop=Aalto%20Yliopisto&to_stop=Keilaniemi
```

**Response:**
```json
{
  "routes": [
    {
      "departure_time": "2025-09-16T08:20:13+03:00",
      "arrival_time": "2025-09-16T08:43:16+03:00", 
      "duration_seconds": 1383,
      "legs": [
        {
          "mode": "WALK",
          "from_place": "Origin",
          "to_place": "Aalto-yliopisto (M)",
          "departure_time": "2025-09-16T08:20:13+03:00",
          "arrival_time": "2025-09-16T08:22:21+03:00",
          "duration_seconds": 128,
          "distance_meters": 115.52
        },
        {
          "mode": "SUBWAY",
          "route": "M1",
          "route_name": "Kivenlahti - Vuosaari",
          "from_place": "Aalto-yliopisto (M)",
          "to_place": "Matinkylä (M)",
          "departure_time": "2025-09-16T08:23:00+03:00",
          "arrival_time": "2025-09-16T08:31:00+03:00"
        }
      ]
    }
  ],
  "from_stop": "Aalto Yliopisto",
  "to_stop": "Keilaniemi", 
  "arrival_time": "20250916084500"
}
```

## Prerequisites

1. **HSL Digitransit API Key** (free registration required):
   - Go to https://portal-api.digitransit.fi/
   - Sign up for a free account
   - Subscribe to the "Routing API" product
   - Copy your subscription key

2. **AWS Account** with CDK configured:
   ```bash
   npm install -g aws-cdk
   cdk bootstrap
   ```

3. **Python 3.11** and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Local Development

1. **Set Environment Variable:**
   ```bash
   export DIGITRANSIT_API_KEY="your-api-key-here"
   ```

2. **Run Local Server:**
   ```bash
   python local_server.py
   ```
   
3. **Test the API:**
   ```bash
   # Health check
   curl http://localhost:5000/
   
   # Test Andrea's commute
   curl "http://localhost:5000/test"
   
   # Custom query
   curl "http://localhost:5000/routes?arrival_time=20250916084500&from_stop=Aalto%20Yliopisto&to_stop=Keilaniemi"
   ```

## AWS Deployment

### Step 1: Set API Key in AWS
```bash
aws ssm put-parameter \
  --name "/transit-api/digitransit-api-key" \
  --value "your-digitransit-api-key" \
  --type "SecureString" \
  --description "Digitransit API key for HSL route planning"
```

### Step 2: Deploy with CDK
```bash
# Synthesize CloudFormation template
cdk synth

# Deploy to AWS
cdk deploy TransitApiStack
```

### Step 3: Get API Gateway URL
After deployment, CDK will output the API Gateway URL. Use this URL to make requests:
```
https://your-api-id.execute-api.region.amazonaws.com/prod/routes?arrival_time=20250916084500
```

## Architecture

- **AWS Lambda**: Runs the Python route planning logic
- **API Gateway**: Provides REST interface with CORS support
- **SSM Parameter Store**: Securely stores the Digitransit API key
- **HSL Digitransit API**: Provides real-time Helsinki transit data

## Next Steps for Email Scheduling

To complete Andrea's requirement for weekday 08:45 email notifications, consider adding:

1. **SES Configuration**: Set up AWS SES for email sending
2. **EventBridge Rule**: Schedule Mon-Fri email sends at appropriate time
3. **Email Lambda**: Fetch routes and format email content
4. **Email Template**: HTML template for route information

Example EventBridge schedule for 06:00 weekdays:
```
cron(0 6 ? * MON-FRI *)
```

## Security Notes

- API key is stored securely in SSM Parameter Store
- Lambda has minimal IAM permissions (only SSM read access)
- API Gateway includes CORS configuration
- No sensitive data is logged or exposed

## Troubleshooting

- **401 Errors**: Check that your Digitransit API key is valid and properly set in SSM
- **No Routes Found**: Verify coordinates and that the requested time is reasonable
- **Timeout Errors**: HSL API may be slow; consider increasing Lambda timeout
- **CDK Deployment Issues**: Ensure you have proper AWS permissions and CDK is bootstrapped