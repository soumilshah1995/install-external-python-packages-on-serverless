import json

def hello(event, context):

    response = {
        "statusCode": 200,
        "body": json.dumps("Hello")
    }

