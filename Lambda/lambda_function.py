import boto3
from botocore.exceptions import ClientError
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

# Custom encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to int if it's an integer, else to float
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def handle_get(event):
    # Extract the key from the API Gateway event (e.g., query parameters)
    query_params = event.get('queryStringParameters', {})
    partition_key = query_params.get('id', None)  # Replace 'key' with your partition key name

    if not partition_key:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required query parameter'})
        }

    try:
        dynamodb = boto3.resource('MY_STORAGE')
        table = dynamodb.Table('MY_TABLE')

        # Query the table for the latest 10,000 items for the provided key
        response = table.query(
            KeyConditionExpression=Key('id').eq(partition_key),  # Replace with your partition key name
            Limit=10000,  # Fetch up to 10,000 entries
            ScanIndexForward=True  # Fetch the first items first
        )
            
        items = response.get('Items', [])

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
            'body': json.dumps({'error': str(e)})
        }


def handle_post(event):
    try:
        dynamodb = boto3.resource('MY_STORAGE')
        table = dynamodb.Table('MY_TABLE')

        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        temperature = body.get('temperature')
        humidity = body.get('humidity')
        id = body.get('id')
        timestamp = body.get('timestamp')

        if temperature is None or humidity is None or id is None or timestamp is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields: temperature, humidity'})
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
            'body': json.dumps({'message': 'Data added successfully', 'timestamp': timestamp, 'id': id})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
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
            'body': json.dumps({'error': 'Method Not Allowed'})
        }