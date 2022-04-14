import json
import os
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):

    username = ""
    return_code = {}
    data = json.loads(event['body'])
    
    if 'username' in data:
        username = data['username']
    elif 'last' in data:
        username = data['last']
    else:
        print("Validation Failed")
        username = "anonymous"
        return_code = json.dumps("ERROR: No 'username' or 'last' sent as key")
        
    if 'username' in data:
        timeEpoch = event['requestContext']['timeEpoch']
        datetime = event['requestContext']['time']
        accountId = event['requestContext']['accountId']
        sourceIp = event['requestContext']['http']['sourceIp']
        userAgent = event['requestContext']['http']['userAgent']
    
        item = {
            'timestamp': timeEpoch,
            'username': username,
            'datetime': datetime,
            'accountId': accountId,
            'sourceIp': sourceIp,
            'userAgent': userAgent
        }

        return_code = put_log(item)
    
    
    if 'last' in data:
        return_code = last_login(username)


    return return_code



def last_login(username):

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    response = table.query(
        IndexName='username',
        KeyConditionExpression=Key('username').eq(username)
    )
    
    last_logins = []
    
    try:
        for login in response['Items']:
            last_logins.append(login['username'] + ": " + login['datetime'])
    except:
        raise
    else:
        return_code = {
            'statusCode': 200,
            'body': json.dumps(last_logins)
        }

    return return_code

def put_log(item):

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    # write the todo to the database
    table.put_item(Item=item)

    return_code = {
        'statusCode': 200,
        'body': json.dumps(item)
    }
    
    return return_code

