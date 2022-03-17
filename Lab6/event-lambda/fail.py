import json


def fail_handler(event, context):

    print("Iam in fail ")
    print(event)
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
