import boto3
import json

client = boto3.client(
    "lambda",
    aws_access_key_id="XXXXXXXXXXXXX",
    aws_secret_access_key="XXXX",
    region_name="us-east-1",
)


response = client.invoke_async(
    FunctionName='event-bus-lambda-dev-hello',
    InvokeArgs=json.dumps({
        'Status': 123
    })
)
print(response)