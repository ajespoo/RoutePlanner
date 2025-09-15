
import json
import os
import sys
from urllib.parse import unquote_plus
import logging

sys.path.insert(0, os.path.dirname(__file__))

from app import app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        # Extract request information
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string_parameters = event.get('queryStringParameters') or {}
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Convert headers to lowercase (Flask expects lowercase)
        flask_headers = {}
        for key, value in headers.items():
            flask_headers[key.lower()] = value
        
        # Build query string
        query_string = ''
        if query_string_parameters:
            query_params = []
            for key, value in query_string_parameters.items():
                if value is not None:
                    query_params.append(f"{key}={unquote_plus(str(value))}")
            if query_params:
                query_string = '?' + '&'.join(query_params)
        
        full_path = path + query_string
        
        logger.info(f"Processing request: {http_method} {full_path}")
        
        # Create a test client and make the request
        with app.test_client() as client:
            if http_method == 'GET':
                response = client.get(full_path, headers=flask_headers)
            elif http_method == 'POST':
                response = client.post(full_path, data=body, headers=flask_headers)
            elif http_method == 'PUT':
                response = client.put(full_path, data=body, headers=flask_headers)
            elif http_method == 'DELETE':
                response = client.delete(full_path, headers=flask_headers)
            else:
                return {
                    'statusCode': 405,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': f'Method {http_method} not allowed'})
                }
        
        # Extract response data
        response_headers = dict(response.headers)
        response_headers['Access-Control-Allow-Origin'] = '*'
        response_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return {
            'statusCode': response.status_code,
            'headers': response_headers,
            'body': response.get_data(as_text=True)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'error_code': 'LAMBDA_ERROR'
            })
        }
