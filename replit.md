# Helsinki Transit Route Planner

## Overview

A Flask-based web application that provides transit route planning for Helsinki public transportation system. The application integrates with the Digitransit API to search for stops and plan routes between locations. It features both a web interface and REST API endpoints, with deployment capabilities to AWS Lambda using CDK infrastructure-as-code.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates served by Flask
- **UI Framework**: Bootstrap with dark theme for responsive design
- **Client-Side**: JavaScript for form handling and API interactions
- **Icons**: Font Awesome for visual elements

### Backend Architecture
- **Web Framework**: Flask with Blueprint-based modular routing
- **Application Structure**: 
  - `app.py` - Main Flask application factory
  - `routes.py` - API and web route handlers organized in blueprints
  - `main.py` and `lambda_handler.py` - Entry points for local and AWS deployment
- **Session Management**: Flask sessions with configurable secret key
- **Request Handling**: ProxyFix middleware for proper header handling behind proxies

### API Design
- **RESTful Endpoints**: `/api/routes` for transit route planning
- **Query Parameters**: Support for from/to stops and arrival time specifications
- **Error Handling**: Structured JSON error responses with error codes
- **CORS**: Enabled for cross-origin requests

### External Service Integration
- **Digitransit Client**: Custom wrapper for Helsinki's GraphQL transit API
- **GraphQL Queries**: Stop search and route planning functionality
- **Error Resilience**: Request timeout and error handling for external API calls

### Deployment Architecture
- **Local Development**: Direct Flask development server
- **AWS Lambda**: Serverless deployment with API Gateway integration
- **Infrastructure as Code**: AWS CDK for reproducible deployments
- **Environment Configuration**: Environment variables for API keys and secrets

### Logging and Monitoring
- **Structured Logging**: Python logging module with appropriate levels
- **AWS CloudWatch**: Lambda function logs with one-week retention
- **Request Tracing**: HTTP method and path logging for debugging

## External Dependencies

### Third-Party APIs
- **Digitransit API**: Helsinki transit data via GraphQL endpoint at api.digitransit.fi
  - Requires API subscription key for authentication
  - Provides stop search and route planning capabilities

### Python Libraries
- **Flask**: Web framework for HTTP handling and templating
- **Requests**: HTTP client for external API communication
- **AWS CDK**: Infrastructure deployment and management
- **Werkzeug**: WSGI utilities including ProxyFix middleware

### AWS Services
- **Lambda**: Serverless compute for application hosting
- **API Gateway**: HTTP API management with CORS support
- **CloudWatch Logs**: Centralized logging and monitoring

### Frontend Dependencies
- **Bootstrap**: CSS framework for responsive UI design
- **Font Awesome**: Icon library for visual elements
- **CDN Delivery**: External CSS/JS resources via CDN links

### Development Tools
- **AWS CDK**: Infrastructure as code with Python bindings
- **Environment Variables**: Configuration management for secrets and API keys