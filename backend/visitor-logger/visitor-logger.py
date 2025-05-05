import json
import boto3
import uuid
import urllib3
from datetime import datetime
from decimal import Decimal

# Initialize services
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VisitorLogs')
http = urllib3.PoolManager()

# Dictionary of country flags
COUNTRY_FLAGS = {
    'Brazil': '🇧🇷',
    'United States': '🇺🇸',
    'Germany': '🇩🇪',
    'India': '🇮🇳',
    'United Kingdom': '🇬🇧',
    'Spain': '🇪🇸',
    'France': '🇫🇷',
    'Japan': '🇯🇵',
    'Italy': '🇮🇹',
    'Canada': '🇨🇦',
    'Australia': '🇦🇺',
    'China': '🇨🇳',
    'Russia': '🇷🇺',
    'Mexico': '🇲🇽',
    'Argentina': '🇦🇷',
    'Netherlands': '🇳🇱',
    'Portugal': '🇵🇹',
    'Switzerland': '🇨🇭',
    'Sweden': '🇸🇪',
    'Norway': '🇳🇴',
    'Denmark': '🇩🇰',
    'Finland': '🇫🇮',
    'Ireland': '🇮🇪',
    'New Zealand': '🇳🇿',
    'Singapore': '🇸🇬',
    'South Korea': '🇰🇷',
    'South Africa': '🇿🇦',
    'Thailand': '🇹🇭',
    'United Arab Emirates': '🇦🇪',
    'Saudi Arabia': '🇸🇦',
    'Poland': '🇵🇱',
    'Austria': '🇦🇹',
    'Belgium': '🇧🇪',
    'Greece': '🇬🇷',
    'Israel': '🇮🇱',
    'Turkey': '🇹🇷',
    'Egypt': '🇪🇬',
    'Vietnam': '🇻🇳',
    'Indonesia': '🇮🇩',
    'Malaysia': '🇲🇾',
    'Philippines': '🇵🇭',
    'Chile': '🇨🇱',
    'Colombia': '🇨🇴',
    'Peru': '🇵🇪',
    'Ukraine': '🇺🇦',
    'Romania': '🇷🇴',
    'Czech Republic': '🇨🇿',
    'Hungary': '🇭🇺',
    'Hong Kong': '🇭🇰',
    'Taiwan': '🇹🇼'
}

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def ip_logged_recently(ip, hours=12):
    """Check if the IP has been logged within the specified time period"""
    try:
        # Calculate the timestamp threshold (e.g., 12 hours ago)
        from datetime import timedelta
        threshold_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        # Query for recent entries from this IP
        response = table.query(
            IndexName='ip-timestamp-index',  # You'll need to create this GSI
            KeyConditionExpression='ip = :ip AND #ts > :threshold',
            ExpressionAttributeNames={
                '#ts': 'timestamp'
            },
            ExpressionAttributeValues={
                ':ip': ip,
                ':threshold': threshold_time
            },
            Limit=1  # Only need to know if at least one exists
        )
        
        # If any items found, this IP has been logged recently
        return len(response.get('Items', [])) > 0
    except Exception as e:
        print(f"Error checking recent IP logs: {e}")
        # If there's an error, log it anyway to be safe
        return False

def get_geolocation_from_ip(ip):
    """Get geolocation data from IP address using free ipinfo.io service"""
    try:
        response = http.request('GET', f'https://ipinfo.io/{ip}/json')
        if response.status == 200:
            geo_data = json.loads(response.data.decode('utf-8'))
            print(f"IP geolocation response: {geo_data}")
            
            # Map ISO country codes to full country names
            country_map = {
                'BR': 'Brazil',
                'US': 'United States',
                'DE': 'Germany',
                'IN': 'India',
                'GB': 'United Kingdom',
                'ES': 'Spain',
                'FR': 'France',
                'JP': 'Japan',
                'IT': 'Italy',
                'CA': 'Canada',
                'AU': 'Australia',
                'CN': 'China',
                'RU': 'Russia',
                'MX': 'Mexico',
                'AR': 'Argentina',
                'NL': 'Netherlands',
                'PT': 'Portugal',
                'CH': 'Switzerland',
                'SE': 'Sweden',
                'NO': 'Norway',
                'DK': 'Denmark',
                'FI': 'Finland',
                'IE': 'Ireland',
                'NZ': 'New Zealand',
                'SG': 'Singapore',
                'KR': 'South Korea',
                'ZA': 'South Africa',
                'TH': 'Thailand',
                'AE': 'United Arab Emirates',
                'SA': 'Saudi Arabia',
                'PL': 'Poland',
                'AT': 'Austria',
                'BE': 'Belgium',
                'GR': 'Greece',
                'IL': 'Israel',
                'TR': 'Turkey',
                'EG': 'Egypt',
                'VN': 'Vietnam',
                'ID': 'Indonesia',
                'MY': 'Malaysia',
                'PH': 'Philippines',
                'CL': 'Chile',
                'CO': 'Colombia',
                'PE': 'Peru',
                'UA': 'Ukraine',
                'RO': 'Romania',
                'CZ': 'Czech Republic',
                'HU': 'Hungary',
                'HK': 'Hong Kong',
                'TW': 'Taiwan'
            }
            
            # Get country name from code or use the provided country code
            country_code = geo_data.get('country', '')
            country = country_map.get(country_code, country_code)
            
            return {
                'country': country or geo_data.get('country', 'Unknown'),
                'city': geo_data.get('city', 'Unknown'),
                'region': geo_data.get('region', 'Unknown')
            }
    except Exception as e:
        print(f"Error getting geolocation data: {e}")
    
    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown'
    }

def lambda_handler(event, context):
    try:
        # Print full event for debugging
        print(f"Full event: {json.dumps(event)}")
        
        # Get headers directly from the event - try different casing as API Gateway can be inconsistent
        headers = event.get('headers', {}) or {}
        headers = {k.lower(): v for k, v in headers.items()}  # Convert all keys to lowercase for consistency
        
        print(f"Headers after normalization: {json.dumps(headers)}")
        
        # Get IP address from different possible sources
        ip = 'Unknown'
        
        # Try X-Forwarded-For header first
        if 'x-forwarded-for' in headers:
            ip = headers['x-forwarded-for'].split(',')[0].strip()
        # Then try the source IP from requestContext
        elif event.get('requestContext', {}).get('identity', {}).get('sourceIp'):
            ip = event['requestContext']['identity']['sourceIp']
        # Finally try the newer API Gateway HTTP API format
        elif event.get('requestContext', {}).get('http', {}).get('sourceIp'):
            ip = event['requestContext']['http']['sourceIp']
        
        # Check if this IP has been logged recently
        if ip != 'Unknown':
            if ip_logged_recently(ip, hours=24):
                print(f"IP {ip} was already logged within the last 24 hours, skipping.")
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': 'https://lucas-albuquerque.com',
                        'Access-Control-Allow-Methods': 'GET',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({
                        'message': 'Visitor already logged',
                        'visitor': 'returning',
                    }, cls=DecimalEncoder)
                }
        
        # Get geolocation data based on IP
        geo_data = get_geolocation_from_ip(ip)
        country = geo_data['country']
        city = geo_data['city']
        
        # Get appropriate flag emoji or default to globe
        flag = COUNTRY_FLAGS.get(country, '🌎')
        
        # Create visitor record
        item = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'ip': ip,
            'country': country,
            'flag': flag,
            'city': city
        }
        
        # Log for debugging
        print(f"Recording visitor: {json.dumps(item)}")
        
        # Store in DynamoDB
        table.put_item(Item=item)
        
        # Only update total count for new visitors (not returning ones)
        # Update total count
        try:
            response = table.update_item(
                Key={'id': 'TOTAL_COUNT'},
                UpdateExpression='SET #count = if_not_exists(#count, :zero) + :incr',
                ExpressionAttributeNames={
                    '#count': 'count'
                },
                ExpressionAttributeValues={
                    ':incr': 1,
                    ':zero': 0
                },
                ReturnValues='UPDATED_NEW'
            )
            total_count = response.get('Attributes', {}).get('count', 0)
        except Exception as count_error:
            print(f"Error updating count: {count_error}")
            total_count = 0

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'https://lucas-albuquerque.com',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Visitor logged successfully',
                'visitor': {
                    'country': country,
                    'flag': flag,
                    'city': city
                },
                'totalCount': total_count
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': 'https://lucas-albuquerque.com',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)}, cls=DecimalEncoder)
        }
