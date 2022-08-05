# must be called as we're using zipped requirements
try:
    import unzip_requirements
except ImportError:
    pass

try:
    import json
    import boto3
    import io
    import pandas as pd

except Exception as e:
    print("Error ***", e)




def hello(event, context):

    client = boto3.client('s3',aws_access_key_id="XXX", aws_secret_access_key="XXXX", region_name="us-east-1",  )

    for item in event.get("Records"):
        s3 = item.get("s3")
        bucket = s3.get("bucket").get("name")
        key = s3.get("object").get("key")

        print("bucket", bucket)
        print("key", key)

        response_new = client.get_object(Bucket=bucket, Key=str(key))
        df = pd.read_csv(io.BytesIO(response_new["Body"].read()))

        print(df)
        print("\n")
        print(df.shape)

    response = {
        "statusCode": 200,
        "body": json.dumps("Process complete ")
    }

