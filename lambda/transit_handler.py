import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for transit route planning
    Expected query parameters:
    - arrival_time: yyyyMMddHHmmss format
    - from_stop: name of departure stop
    - to_stop: name of destination stop
    """
    
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        arrival_time = query_params.get('arrival_time')
        from_stop = query_params.get('from_stop', 'Aalto Yliopisto')
        to_stop = query_params.get('to_stop', 'Keilaniemi')
        
        if not arrival_time:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'arrival_time parameter is required (format: yyyyMMddHHmmss)'
                })
            }
        
        # Convert arrival time to proper format for HSL GraphQL API
        try:
            arrival_dt = datetime.strptime(arrival_time, '%Y%m%d%H%M%S')
            # HSL API expects local time without timezone offset + separate timeZone field
            arrival_iso = arrival_dt.isoformat()
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid arrival_time format. Use yyyyMMddHHmmss'
                })
            }
        
        # Get route information from HSL API
        routes = get_transit_routes(from_stop, to_stop, arrival_iso)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'routes': routes,
                'from_stop': from_stop,
                'to_stop': to_stop,
                'arrival_time': arrival_time
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


def get_transit_routes(from_stop: str, to_stop: str, arrival_time: str) -> List[Dict[str, Any]]:
    """
    Query HSL GraphQL API for transit routes
    """
    
    # Updated coordinates based on HSL data
    stop_coordinates = {
        'Aalto Yliopisto': {'lat': 60.1846, 'lon': 24.82554},  # HSL:2000102 - Aalto metro station
        'Keilaniemi': {'lat': 60.175294, 'lon': 24.684855},   # Near KONE building in Keilaniemi
        'KONE Building': {'lat': 60.175294, 'lon': 24.684855}
    }
    
    from_coords = stop_coordinates.get(from_stop, stop_coordinates['Aalto Yliopisto'])
    to_coords = stop_coordinates.get(to_stop, stop_coordinates['Keilaniemi'])
    
    # GraphQL query for route planning with arrival time constraint
    query = """
    {
      planConnection(
        origin: {location: {coordinate: {latitude: %s, longitude: %s}}}
        destination: {location: {coordinate: {latitude: %s, longitude: %s}}}
        dateTime: {latestArrival: "%s", timeZone: "Europe/Helsinki"}
        first: 3
      ) {
        edges {
          node {
            start
            end
            duration
            legs {
              mode
              duration
              distance
              start {
                scheduledTime
              }
              end {
                scheduledTime
              }
              from {
                name
              }
              to {
                name
              }
              trip {
                route {
                  shortName
                  longName
                }
              }
            }
          }
        }
      }
    }
    """ % (from_coords['lat'], from_coords['lon'], 
           to_coords['lat'], to_coords['lon'], arrival_time)
    
    try:
        hsl_api_url = os.getenv('HSL_API_URL', 'https://api.digitransit.fi/routing/v2/hsl/gtfs/v1')
        
        # Get API key from SSM Parameter Store or environment
        api_key = None
        if os.getenv('DIGITRANSIT_API_KEY_PARAM'):
            try:
                import boto3
                ssm_client = boto3.client('ssm')
                response = ssm_client.get_parameter(
                    Name=os.getenv('DIGITRANSIT_API_KEY_PARAM'),
                    WithDecryption=True
                )
                api_key = response['Parameter']['Value']
            except Exception:
                pass  # Fall back to env var
        
        if not api_key:
            api_key = os.getenv('DIGITRANSIT_API_KEY')
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Only add API key header if we have one (API works without key but with rate limits)
        if api_key and api_key != 'PLACEHOLDER_SET_MANUALLY':
            headers['digitransit-subscription-key'] = api_key
        
        response = requests.post(
            hsl_api_url,
            json={'query': query},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            routes = []
            
            # Debug: check the full response structure
            if 'data' in data and data['data'] and data['data'].get('planConnection'):
                plan_connection = data['data']['planConnection']
                if plan_connection.get('edges'):
                    for edge in plan_connection['edges']:
                        route_info = {
                            'departure_time': edge['node']['start'],
                            'arrival_time': edge['node']['end'],
                            'duration_seconds': edge['node']['duration'],
                            'legs': []
                        }
                        
                        for leg in edge['node']['legs']:
                            leg_info = {
                                'mode': leg['mode'],
                                'duration_seconds': leg['duration'],
                                'distance_meters': leg.get('distance', 0),
                                'departure_time': leg['start']['scheduledTime'],
                                'arrival_time': leg['end']['scheduledTime'],
                                'from_place': leg.get('from', {}).get('name', 'Unknown'),
                                'to_place': leg.get('to', {}).get('name', 'Unknown'),
                                'route': leg['trip']['route']['shortName'] if leg.get('trip') and leg['trip'].get('route') else None,
                                'route_name': leg['trip']['route']['longName'] if leg.get('trip') and leg['trip'].get('route') else None
                            }
                            route_info['legs'].append(leg_info)
                        
                        routes.append(route_info)
                else:
                    # No routes found - this might be normal
                    routes = [{'info': 'No routes found for the specified time/locations', 'api_response': data}]
            else:
                # Error in API response format
                routes = [{'error': 'Invalid API response format', 'api_response': data}]
            
            return routes
        else:
            return [{'error': f'HSL API error: {response.status_code}', 'response_text': response.text[:500]}]
            
    except Exception as e:
        return [{'error': f'Failed to fetch routes: {str(e)}'}]