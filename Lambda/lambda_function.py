import boto3
from botocore.exceptions import ClientError
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import logging

# Initialize Logger
logger = logging.getLogger()
logger.setLevel("INFO")

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MY_TABLE')

# Custom encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to int if it's an integer, else to float
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def add_one_hour_to_timestamp(timestamp):
    # Convert Unix timestamp to datetime object (in UTC)
    timestamp_dt = datetime.utcfromtimestamp(int(timestamp))
    # Add one hour to adjust for the timezone offset (e.g., UTC+1 like Irland where storage is located)
    adjusted_timestamp = timestamp_dt + timedelta(hours=1)
    # Return the adjusted timestamp in ISO 8601 format (with 'Z' to indicate UTC)
    return adjusted_timestamp.isoformat() + 'Z'

def handle_get(event):
    # Parse the request body
    query_params = event.get('queryStringParameters', {})
    start = query_params.get('start')
    end = query_params.get('end')
    partition_key = query_params.get('id', None)

    if not partition_key:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'error': 'Missing required query parameter'})
        }

    # Get the current UTC time (timezone-aware)
    now_utc = datetime.now(timezone.utc)
    
    # Set default range: now to 30 days ago
    if not end:
        end = int(now.timestamp())
    if not start:
        start = int((now - timedelta(days=30)).timestamp())
        
    try:
        # Convert Unix timestamps to ISO 8601 string format
        start_date = add_one_hour_to_timestamp(int(start))
        end_date = add_one_hour_to_timestamp(int(end))

        logger.info("Query arguments: id: " + partition_key + " start: " + start_date + " end: " + end_date)

        # Query DynamoDB
        response = table.scan(
            FilterExpression="#deviceId = :deviceId AND #timestamp BETWEEN :start AND :end",
            ExpressionAttributeNames={
                "#deviceId": "id",
                "#timestamp": "timestamp"
            },
            ExpressionAttributeValues={
                ":deviceId": partition_key,
                ":start": start_date,
                ":end": end_date
            }
        )

        items = response.get('Items', [])

        # Convert the timestamp in the database to UTC and return the results
        for item in items:
                    if 'Timestamp' in item:
                        # Ensure the timestamp is correctly in UTC when processing
                        item['Timestamp'] = datetime.datetime.fromisoformat(item['Timestamp']).astimezone(datetime.timezone.utc).isoformat()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps(items, cls=DecimalEncoder)  # Use the custom encoder
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'error': str(e)})
        }


def handle_post(event):
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        temperature = body.get('temperature')
        humidity = body.get('humidity')
        id = body.get('id')
        timestamp = body.get('timestamp')

        if temperature is None or humidity is None or id is None or timestamp is None:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                },
                'body': json.dumps({'error': 'Missing required fields: temperature, humidity'})
            }

        # Validate ISO 8601 timestamp format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                },
                'body': json.dumps({'error': 'Invalid timestamp format. Use ISO 8601 format.'})
            }
            
        # Insert item into DynamoDB
        table.put_item(Item={
            'timestamp': timestamp,
            'id': id,
            'temperature': temperature,
            'humidity': humidity
        })

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'message': 'Data added successfully', 'timestamp': timestamp, 'id': id})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'error': str(e)})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }


def lambda_handler(event, context):
    logger.info('## EVENT')
    logger.info(event)

    # Determine the HTTP method
    http_method = event.get('httpMethod', '').upper()

    if http_method == 'GET':
        # Handle GET request
        return handle_get(event)
    elif http_method == 'POST':
        # Handle POST request
        return handle_post(event)
    else:
        # Unsupported method
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
            'body': json.dumps({'error': 'Method Not Allowed'})
        }