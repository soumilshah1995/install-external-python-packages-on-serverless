try:
    import os
    import re
    import json
    import boto3
    import uuid
    import json
    from io import StringIO
    from dateutil.parser import parse
except Exception as e:
    print("Error : {}".format(e))


class AWSS3(object):
    """Helper class to which add functionality on top of boto3 """

    def __init__(self, bucket, aws_access_key_id, aws_secret_access_key, region_name):

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
            print("Error : {} ".format(e))
            return "error"

    def item_exists(self, Key):
        """Given key check if the items exists on AWS S3 """
        try:
            response_new = self.client.get_object(Bucket=self.BucketName, Key=str(Key))
            return True
        except Exception as e:
            return False

    def get_item(self, Key):

        """Gets the Bytes Data from AWS S3 """

        try:
            response_new = self.client.get_object(Bucket=self.BucketName, Key=str(Key))
            return response_new["Body"].read()

        except Exception as e:
            print("Error :{}".format(e))
            return False

    def find_one_update(self, data=None, key=None):

        """
        This checks if Key is on S3 if it is return the data from s3
        else store on s3 and return it
        """

        flag = self.item_exists(Key=key)

        if flag:
            data = self.get_item(Key=key)
            return data

        else:
            self.put_files(Key=key, Response=data)
            return data

    def delete_object(self, Key):

        response = self.client.delete_object(Bucket=self.BucketName, Key=Key, )
        return response

    def get_all_keys(self, Prefix=""):

        """
        :param Prefix: Prefix string
        :return: Keys List
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.BucketName, Prefix=Prefix)

            tmp = []

            for page in pages:
                for obj in page["Contents"]:
                    tmp.append(obj["Key"])

            return tmp
        except Exception as e:
            return []

    def print_tree(self):
        keys = self.get_all_keys()
        for key in keys:
            print(key)
        return None

    def find_one_similar_key(self, searchTerm=""):
        keys = self.get_all_keys()
        return [key for key in keys if re.search(searchTerm, key)]

    def __repr__(self):
        return "AWS S3 Helper class "


class HistoricalDataDump(AWSS3):
    def __init__(self, data):
        self.data = data
        AWSS3.__init__(self,
                       aws_access_key_id=os.getenv("APP_AWS_ACCESS_KEY"),
                       aws_secret_access_key=os.getenv("APP_AWS_SECRET_KEY"),
                       region_name=os.getenv("APP_AWS_REGION_NAME"),
                       bucket=os.getenv("S3_BUCKET"),
                       )
        self.table_name = "mongo_data"

    def flatten_dict(self, data, parent_key='', sep='_'):
        """Flatten data into a single dict"""
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key

            if type(value) == dict:
                items.extend(self.flatten_dict(value, new_key, sep=sep).items())
            else:
                items.append((new_key, value))

        return dict(items)

    def dict_clean(self, items):
        result = {}
        for key, value in items:
            if value is None:
                value = 'n/a'
            if value == "None":
                value = 'n/a'
            if value == "null":
                value = 'n/a'
            if len(str(value)) < 1:
                value = 'n/a'
            result[key] = str(value)
        return result

    def mongo_to_s3(self):

        """Flatten data into a single dict"""
        clean_messages = [self.flatten_dict(message) for message in self.data.get("data")]
        clean_messages_new = [json.loads(json.dumps(message), object_pairs_hook=self.dict_clean) for message in
                              clean_messages]
        response = self.put_json_file_to_s3(data=clean_messages_new)
        print("""Successfully uploading the record.""")

    def put_json_file_to_s3(self, data=[]):
        """Put the json object to S3"""
        try:
            dt = parse(data[0].get("createdAt"))
            csv_buffer = StringIO()

            records = ""
            for record in data: records += json.dumps(record) + "\n"

            new_s3_path = "database=mongodb/tablename={}/year={}/month={}/day={}/{}.json".format(
                self.table_name, dt.year, dt.month, dt.day, uuid.uuid4().__str__()
            )
            csv_buffer.write(records)
            csv_buffer.seek(0)
            self.put_files(Response=csv_buffer.getvalue(), Key=new_s3_path)

        except Exception:
            raise Exception("Uploading records failed")


def lambda_handler(event, context):
    messages = [json.loads(record.get("body")) for record in event['Records']]

    for message in messages:
        helper = HistoricalDataDump(data=message)
        helper.mongo_to_s3()

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully uploaded records!!')
    }
