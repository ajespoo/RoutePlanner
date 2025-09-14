# Transit API

## Overview
This is a REST API designed specifically for Helsinki transit route planning, with a focus on Andrea's daily commute from Aalto University to KONE Building in Keilaniemi. The API integrates with HSL's Digitransit GraphQL service to provide real-time transit routing with arrival time constraints. The system is architected for AWS Lambda deployment using CDK infrastructure as code.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### API Design
- **REST API Pattern**: Simple GET endpoint `/routes` with query parameters for arrival time and stop names
- **Query Parameter Format**: Uses `yyyyMMddHHmmss` format for arrival times to ensure consistent parsing
- **Default Route Configuration**: Hardcoded defaults for Aalto University to Keilaniemi commute to reduce API complexity

### Backend Architecture
- **AWS Lambda**: Serverless function architecture for cost-effective, auto-scaling compute
- **Python Runtime**: Python 3.11 runtime chosen for strong datetime handling and HTTP client libraries
- **CDK Infrastructure**: Infrastructure as Code using AWS CDK for reproducible deployments
- **API Gateway**: REST API Gateway for HTTP request handling and CORS management

### Data Processing
- **GraphQL Integration**: Communicates with HSL Digitransit GraphQL API for real-time transit data
- **Arrival Time Constraints**: Implements reverse route planning (specify arrival time, get departure time)
- **Response Transformation**: Converts GraphQL responses to simplified REST JSON format

### Security and Configuration
- **AWS SSM Parameter Store**: Secure storage for Digitransit API keys
- **IAM Permissions**: Lambda function granted read-only access to specific SSM parameters
- **Environment Variables**: Configuration through Lambda environment variables for API URLs

### Local Development
- **Flask Development Server**: Local testing environment that imports Lambda handler code
- **Shared Code Base**: Lambda handler can be imported and tested locally without duplication
- **Health Check Endpoint**: Root endpoint provides API status and usage examples

### Error Handling
- **Input Validation**: Validates arrival time format and required parameters
- **HTTP Status Codes**: Proper 400/500 error responses with descriptive messages
- **CORS Support**: Cross-origin resource sharing enabled for web client integration

## External Dependencies

### Primary Integration
- **HSL Digitransit API**: GraphQL endpoint at `api.digitransit.fi` for Helsinki transit route planning
- **API Authentication**: Requires Digitransit API key stored in AWS SSM Parameter Store

### AWS Services
- **AWS Lambda**: Serverless compute platform for API execution
- **API Gateway**: HTTP API management and routing
- **SSM Parameter Store**: Secure configuration and secrets management
- **IAM**: Identity and access management for service permissions

### Development Dependencies
- **AWS CDK**: Infrastructure as Code framework for AWS resource provisioning
- **Flask**: Local development server for testing API endpoints
- **Requests**: HTTP client library for external API calls
- **Boto3**: AWS SDK for Python for SSM parameter access

### Runtime Requirements
- **Python 3.11**: Lambda runtime environment
- **aws-cdk-lib**: CDK constructs and AWS service integrations
- **aws-lambda-python-alpha**: CDK Python Lambda function constructs