try:
    import json
    import json
    import boto3
    import base64
    import os
    import datetime
    import uuid
    from datetime import datetime
    from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
except Exception as e:
    print("Error : {} ".format(e))

def unmarshall(dynamo_obj: dict) -> dict:
    """Convert a DynamoDB dict into a standard dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}


def marshall(python_obj: dict) -> dict:
    """Convert a standard dict into a DynamoDB ."""
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}

class AWSS3(object):
    """Helper class to which add functionality on top of boto3 """

    def __init__(
            self,
            bucket=os.getenv("bucketname"),
            aws_access_key_id=os.getenv("DEV_AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("DEV_AWS_SECRET_KEY"),
            region_name=os.getenv("DEV_AWS_REGION_NAME"),
    ):
        self.BucketName = bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def put_files(self, Response=None, Key=None):
        """
        Put the File on S3
        :return: Bool
        """
        try:
            response = self.client.put_object(
                ACL="private", Body=Response, Bucket=self.BucketName, Key=Key
            )
            return "ok"
        except Exception as e:
            raise Exception("Failed to upload records. Error : {}".format(e))

    def item_exists(self, Key):
        """Given key check if the items exists on AWS S3 """
        try:
            response_new = self.client.get_object(
                Bucket=self.BucketName, Key=str(Key))
            return True
        except Exception as e:
            return False

    def get_item(self, Key):
        """Gets the Bytes Data from AWS S3 """
        try:
            response_new = self.client.get_object(
                Bucket=self.BucketName, Key=str(Key))
            return response_new["Body"].read()
        except Exception as e:
            print("Error :{}".format(e))
            return False

class Datetime(object):
    @staticmethod
    def get_year_month_day():
        """
        Return Year month and day
        :return: str str str
        """
        dt = datetime.now()
        year = dt.year
        month = dt.month
        day = dt.day
        return year, month, day


def flatten_dict(data, parent_key='', sep='_'):
    """Flatten data into a single dict"""
    try:
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key
            if type(value) == dict:
                items.extend(flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
    except Exception as e:
        return {}


def lambda_handler(event, context):

    print("event", event)
    print("\n")

    print("Length: {} ".format(len(event['Records'])))

    for record in event['Records']:

        payload = base64.b64decode(record['kinesis']['data'])
        de_serialize_payload = json.loads(payload)

        print("de_serialize_payload", de_serialize_payload, type(de_serialize_payload))

        eventName = de_serialize_payload.get("eventName")
        print("eventName", eventName)


        json_data = None

        if eventName.strip().lower() == "INSERT".lower():
            json_data = de_serialize_payload.get("dynamodb").get("NewImage")

        if eventName.strip().lower() == "REMOVE".lower():
            json_data = de_serialize_payload.get("dynamodb").get("OldImage")

        if json_data is not None:

            json_data_unmarshal = unmarshall(json_data)
            json_data_unmarshal["awsRegion"] = de_serialize_payload.pop("awsRegion")
            json_data_unmarshal["eventID"] = de_serialize_payload.pop("eventID")
            json_data_unmarshal["eventName"] = de_serialize_payload.pop("eventName")
            json_data_unmarshal["eventSource"] = de_serialize_payload.pop("eventSource")


            helper = AWSS3()
            year, month, day = Datetime.get_year_month_day()
            _final_processed_json = flatten_dict(json_data_unmarshal)
            helper.put_files(
                Key="table_name=dynamo_db/year={}/month={}/day={}/{}.json".format(year, month, day, uuid.uuid4().__str__()),
                Response=json.dumps(_final_processed_json)
            )
            print("_final_processed_json", _final_processed_json)


    print("****************  ALL SET *********************")
    print("Length: {} ".format(len(event['Records'])))

