import json


def sucess_handler(event, context):

    print("Iam in success ")
    print(event)
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
