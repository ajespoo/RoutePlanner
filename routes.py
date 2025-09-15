
import os
from flask import Blueprint, request, jsonify, render_template
from digitransit_client import DigitransitClient
import logging

logger = logging.getLogger(__name__)

# Create blueprints
api_bp = Blueprint('api', __name__, url_prefix='/api')
web_bp = Blueprint('web', __name__)

# Initialize Digitransit client
digitransit_client = DigitransitClient()

@web_bp.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@api_bp.route('/routes', methods=['GET'])
def get_routes():
    """Get transit routes between two stops with arrival time"""
    try:
        from_stop = request.args.get('from')
        to_stop = request.args.get('to')
        arrival_time = request.args.get('arrival_time')
        
        # Validate required parameters
        if not from_stop:
            return jsonify({
                'error': 'Missing required parameter: from',
                'error_code': 'MISSING_PARAMETER'
            }), 400
        
        if not to_stop:
            return jsonify({
                'error': 'Missing required parameter: to', 
                'error_code': 'MISSING_PARAMETER'
            }), 400
        
        if not arrival_time:
            return jsonify({
                'error': 'Missing required parameter: arrival_time',
                'error_code': 'MISSING_PARAMETER'
            }), 400
        
        # Validate arrival time format
        if len(arrival_time) != 14 or not arrival_time.isdigit():
            return jsonify({
                'error': 'Invalid arrival_time format. Use yyyyMMddHHmmss',
                'error_code': 'INVALID_DATE_FORMAT'
            }), 400
        
        logger.info(f"Planning route from {from_stop} to {to_stop} arriving at {arrival_time}")
        
        # Plan the route
        result = digitransit_client.plan_route(from_stop, to_stop, arrival_time)
        
        # Check for errors
        if 'error' in result:
            status_code = 400
            if result.get('error_code') == 'STOP_NOT_FOUND':
                status_code = 404
            elif result.get('error_code') == 'API_CONNECTION_ERROR':
                status_code = 503
            elif result.get('error_code') == 'INTERNAL_ERROR':
                status_code = 500
            
            return jsonify(result), status_code
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_routes: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/stops/search', methods=['GET'])
def search_stops():
    """Search for stops by name"""
    try:
        query = request.args.get('q')
        
        if not query:
            return jsonify({
                'error': 'Missing required parameter: q',
                'error_code': 'MISSING_PARAMETER'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'error': 'Query must be at least 2 characters long',
                'error_code': 'QUERY_TOO_SHORT'
            }), 400
        
        logger.info(f"Searching stops for query: {query}")
        
        stops = digitransit_client.search_stops(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'stops': stops,
            'total': len(stops)
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in search_stops: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'error_code': 'INTERNAL_ERROR'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Helsinki Transit API'
    })
