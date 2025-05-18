import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

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
        # Get total count
        try:
            response = table.get_item(Key={'id': 'TOTAL_COUNT'})
            total_count = response.get('Item', {}).get('count', 0)
        except Exception as e:
            print(f"Error getting total count: {e}")
            total_count = 0

        visitor_data = []

        try:
            # Query the GSI to get the latest 5 visitors across all IPs
            # We need to do a "scan" on the GSI if there's no fixed partition key
            response = table.scan(
                IndexName='ip-timestamp-index'
            )

            all_items = response.get('Items', [])

            # Filter out system or irrelevant items
            recent_visitors = [
                item for item in all_items
                if item.get('id') != 'TOTAL_COUNT' and 'timestamp' in item
            ]

            # Sort by timestamp descending
            sorted_visitors = sorted(
                recent_visitors,
                key=lambda x: x['timestamp'],
                reverse=True
            )

            for visitor in sorted_visitors[:5]:
                visitor_data.append({
                    'country': visitor.get('country', 'Unknown'),
                    'city': visitor.get('city', 'Unknown'),
                    'flag': visitor.get('flag', '🌎'),
                    'timestamp': visitor.get('timestamp')
                })

        except Exception as e:
            print(f"Error getting recent visitors via GSI: {e}")
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