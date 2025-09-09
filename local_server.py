from flask import Flask, request, jsonify
import sys
import os

# Add lambda directory to Python path so we can import the handler
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda'))

from transit_handler import get_transit_routes
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Transit API is running',
        'endpoints': [
            '/routes?arrival_time=yyyyMMddHHmmss&from_stop=Aalto Yliopisto&to_stop=Keilaniemi'
        ]
    })

@app.route('/routes', methods=['GET'])
def get_routes():
    """
    Get transit routes based on arrival time and stops
    Query parameters:
    - arrival_time: yyyyMMddHHmmss format (required)
    - from_stop: departure stop name (default: Aalto Yliopisto)  
    - to_stop: destination stop name (default: Keilaniemi)
    """
    try:
        # Get query parameters
        arrival_time = request.args.get('arrival_time')
        from_stop = request.args.get('from_stop', 'Aalto Yliopisto')
        to_stop = request.args.get('to_stop', 'Keilaniemi')
        
        if not arrival_time:
            return jsonify({
                'error': 'arrival_time parameter is required (format: yyyyMMddHHmmss)',
                'example': 'http://localhost:5000/routes?arrival_time=20250909084500&from_stop=Aalto Yliopisto&to_stop=Keilaniemi'
            }), 400
        
        # Validate arrival time format
        try:
            arrival_dt = datetime.strptime(arrival_time, '%Y%m%d%H%M%S')
            arrival_iso = arrival_dt.isoformat()
        except ValueError:
            return jsonify({
                'error': 'Invalid arrival_time format. Use yyyyMMddHHmmss',
                'example': '20250909084500 for Sep 9, 2025 at 08:45:00'
            }), 400
        
        # Get routes using the same logic as the Lambda function
        routes = get_transit_routes(from_stop, to_stop, arrival_iso)
        
        return jsonify({
            'routes': routes,
            'from_stop': from_stop,
            'to_stop': to_stop,
            'arrival_time': arrival_time,
            'query_info': {
                'parsed_time': arrival_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'routes_found': len(routes)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/test', methods=['GET'])
def test_route():
    """Test endpoint with default values for Andrea's commute"""
    # Use tomorrow at 08:45 as default
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    test_time = tomorrow.replace(hour=8, minute=45, second=0, microsecond=0)
    test_time_str = test_time.strftime('%Y%m%d%H%M%S')
    
    routes = get_transit_routes('Aalto Yliopisto', 'Keilaniemi', test_time.isoformat())
    
    return jsonify({
        'message': 'Test route for Andrea\'s daily commute',
        'routes': routes,
        'from_stop': 'Aalto Yliopisto',
        'to_stop': 'Keilaniemi',
        'arrival_time': test_time_str,
        'human_readable_time': test_time.strftime('%Y-%m-%d %H:%M:%S'),
        'routes_found': len(routes)
    })

if __name__ == '__main__':
    print("Starting Transit API server...")
    print("API Documentation:")
    print("- Health check: http://localhost:5000/")
    print("- Get routes: http://localhost:5000/routes?arrival_time=20250909084500&from_stop=Aalto Yliopisto&to_stop=Keilaniemi")
    print("- Test Andrea's commute: http://localhost:5000/test")
    app.run(host='0.0.0.0', port=5000, debug=True)