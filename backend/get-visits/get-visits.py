import json
import boto3
from decimal import Decimal
from datetime import datetime, timedelta

# Initialize services
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('VisitorLogs')

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Get the total count
        try:
            response = table.get_item(Key={'id': 'TOTAL_COUNT'})
            total_count = response.get('Item', {}).get('count', 0)
        except Exception as e:
            print(f"Error getting total count: {e}")
            total_count = 0
        
        # Get recent visitors (last 10 excluding the TOTAL_COUNT item)
        try:
            # Calculate timestamp for recent visitors (e.g., last 7 days)
            cutoff_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
            
            # Query recent visitors
            response = table.scan(
                FilterExpression='attribute_exists(country) AND #id <> :total_id AND #ts > :cutoff',
                ExpressionAttributeNames={
                    '#id': 'id',
                    '#ts': 'timestamp'
                },
                ExpressionAttributeValues={
                    ':total_id': 'TOTAL_COUNT',
                    ':cutoff': cutoff_time
                },
                Limit=10  # Limit to 10 most recent
            )
            
            recent_visitors = response.get('Items', [])
            
            # Sort by timestamp descending (most recent first)
            recent_visitors.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Format the response data
            visitor_data = []
            for visitor in recent_visitors:
                visitor_data.append({
                    'country': visitor.get('country', 'Unknown'),
                    'city': visitor.get('city', 'Unknown'),
                    'flag': visitor.get('flag', '🌎'),
                    'timestamp': visitor.get('timestamp')
                })
                
        except Exception as e:
            print(f"Error getting recent visitors: {e}")
            visitor_data = []

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'https://lucas-albuquerque.com',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'totalCount': total_count,
                'recentVisitors': visitor_data
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
