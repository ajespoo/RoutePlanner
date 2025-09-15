
import os
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class DigitransitClient:
    def __init__(self):
        self.base_url = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
        self.headers = {
            'Content-Type': 'application/json',
            'digitransit-subscription-key': os.environ.get('DIGITRANSIT_API_KEY', '')
        }
    
    def search_stops(self, name: str) -> List[Dict]:
        """Search for stops by name"""
        query = """
        {
          stops(name: "%s") {
            gtfsId
            name
            code
            lat
            lon
            zoneId
          }
        }
        """ % name
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={'query': query},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            return data.get('data', {}).get('stops', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching stops: {e}")
            return []
    
    def find_stop_coordinates(self, stop_name: str) -> Optional[Tuple[float, float]]:
        """Find coordinates for a stop by name"""
        stops = self.search_stops(stop_name)
        if not stops:
            return None
        
        # Return the first match
        stop = stops[0]
        return (stop['lat'], stop['lon'])
    
    def plan_route(self, from_name: str, to_name: str, arrival_time_str: str) -> Dict:
        """Plan route from one stop to another with specific arrival time"""
        try:
            # Parse arrival time
            arrival_time = datetime.strptime(arrival_time_str, '%Y%m%d%H%M%S')
            
            # Find coordinates for stops
            from_coords = self.find_stop_coordinates(from_name)
            to_coords = self.find_stop_coordinates(to_name)
            
            if not from_coords:
                return {
                    'error': f'Stop not found: {from_name}',
                    'error_code': 'STOP_NOT_FOUND'
                }
            
            if not to_coords:
                return {
                    'error': f'Stop not found: {to_name}',
                    'error_code': 'STOP_NOT_FOUND'
                }
            
            # Format time for GraphQL (ISO format with timezone)
            arrival_time_iso = arrival_time.strftime('%Y-%m-%dT%H:%M:%S+03:00')
            
            query = """
            {
              planConnection(
                origin: {location: {coordinate: {latitude: %f, longitude: %f}}, label: "%s"}
                destination: {location: {coordinate: {latitude: %f, longitude: %f}}, label: "%s"}
                first: 5
                dateTime: {latestArrival: "%s"}
              ) {
                pageInfo {
                  endCursor
                }
                edges {
                  node {
                    start
                    end
                    duration
                    legs {
                      from {
                        name
                        lat
                        lon
                        stop {
                          gtfsId
                          code
                        }
                      }
                      to {
                        name
                        lat
                        lon
                        stop {
                          gtfsId
                          code
                        }
                      }
                      start {
                        scheduledTime
                        estimated {
                          time
                        }
                      }
                      end {
                        scheduledTime
                        estimated {
                          time
                        }
                      }
                      mode
                      duration
                      distance
                      route {
                        gtfsId
                        shortName
                        longName
                        mode
                      }
                      trip {
                        gtfsId
                        tripHeadsign
                      }
                      realTime
                      realtimeState
                      intermediateStops {
                        gtfsId
                        name
                      }
                    }
                    emissionsPerPerson {
                      co2
                    }
                  }
                }
              }
            }
            """ % (from_coords[0], from_coords[1], from_name, 
                   to_coords[0], to_coords[1], to_name, arrival_time_iso)
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={'query': query},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return {
                    'error': 'Failed to plan route',
                    'error_code': 'PLANNING_ERROR',
                    'details': data['errors']
                }
            
            connection_data = data.get('data', {}).get('planConnection', {})
            routes = []
            
            for edge in connection_data.get('edges', []):
                route_info = self._format_route_info(edge['node'], from_name, to_name)
                routes.append(route_info)
            
            return {
                'success': True,
                'from': from_name,
                'to': to_name,
                'arrival_time': arrival_time_str,
                'routes': routes,
                'total_routes': len(routes)
            }
            
        except ValueError as e:
            return {
                'error': 'Invalid date format. Use yyyyMMddHHmmss',
                'error_code': 'INVALID_DATE_FORMAT'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'error': 'Failed to connect to transit API',
                'error_code': 'API_CONNECTION_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'error': 'An unexpected error occurred',
                'error_code': 'INTERNAL_ERROR'
            }
    
    def _format_route_info(self, route_node: Dict, from_name: str, to_name: str) -> Dict:
        """Format route information for response"""
        legs_info = []
        
        for leg in route_node.get('legs', []):
            leg_info = {
                'mode': leg.get('mode'),
                'duration': leg.get('duration'),
                'distance': leg.get('distance'),
                'from': {
                    'name': leg.get('from', {}).get('name', ''),
                    'lat': leg.get('from', {}).get('lat'),
                    'lon': leg.get('from', {}).get('lon')
                },
                'to': {
                    'name': leg.get('to', {}).get('name', ''),
                    'lat': leg.get('to', {}).get('lat'),
                    'lon': leg.get('to', {}).get('lon')
                },
                'start_time': leg.get('start', {}).get('scheduledTime'),
                'end_time': leg.get('end', {}).get('scheduledTime'),
                'real_time': leg.get('realTime', False),
                'realtime_state': leg.get('realtimeState')
            }
            
            # Add route information for transit legs
            if leg.get('route'):
                leg_info['route'] = {
                    'id': leg['route'].get('gtfsId'),
                    'short_name': leg['route'].get('shortName'),
                    'long_name': leg['route'].get('longName'),
                    'mode': leg['route'].get('mode')
                }
            
            # Add trip information
            if leg.get('trip'):
                leg_info['trip'] = {
                    'id': leg['trip'].get('gtfsId'),
                    'headsign': leg['trip'].get('tripHeadsign')
                }
            
            legs_info.append(leg_info)
        
        return {
            'start_time': route_node.get('start'),
            'end_time': route_node.get('end'),
            'duration': route_node.get('duration'),
            'legs': legs_info,
            'emissions': route_node.get('emissionsPerPerson', {})
        }
