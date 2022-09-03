try:
    import os
    import pymongo
    from functools import wraps
    from enum import Enum
    import json
    import sys
    import boto3
    import re
    import datetime
    from datetime import datetime

    from dateutil.parser import parse
    from datetime import datetime, timezone, timedelta

    from dotenv import load_dotenv
    load_dotenv("runner.env")

except Exception as e:
    print("Error@@@@@@@@@@@ : {} ".format(e))


class MongoDbSettings(object):
    def __init__(self, connection_string, database_name, collection_name):
        self.connection_string = connection_string
        self.collection_name = collection_name
        self.database_name = database_name


class MongoDB:
    def __init__(self, mongo_db_settings):
        self.mongo_db_settings = mongo_db_settings

        if type(self.mongo_db_settings).__name__ != "MongoDbSettings":
            raise Exception("Please mongo_db_settings  pass correct Instance")

        self.client = pymongo.MongoClient(
            self.mongo_db_settings.connection_string,
            port=27017,
            tls=True,tlsAllowInvalidCertificates=True
        )
        self.cursor = self.client[self.mongo_db_settings.database_name][
            self.mongo_db_settings.collection_name
        ]

    def get_total_count(self, query={}, logger=None):
        total_count = self.cursor.count_documents(filter=query)

        return total_count

    def get_data(self, query={}, sort=pymongo.ASCENDING, mongo_batch_size=int(os.getenv("BATCH_MONGO_CHUNK_SIZE"))):

        # mongo_batch_size = 300

        # print("mongo_batch_size", mongo_batch_size)

        # data = list(self.cursor.find(query).sort("createdAt", sort))

        # return data

        total_count = self.cursor.count_documents(filter=query)
        total_pages = total_count // mongo_batch_size
        page_size = mongo_batch_size

        if total_count % mongo_batch_size != 0:
            total_pages += 1
        for page_number in range(total_pages):
            skips = page_size * page_number
            data = list(self.cursor.find(query).skip(skips).limit(page_size).sort('createdAt', sort))
            yield data

# =================== Connector ==========================================================


class Connector(Enum):
    MONGODB = MongoDB(
        mongo_db_settings=MongoDbSettings(
            connection_string=os.getenv("BATCH_MONGO_DB"),
            database_name=os.getenv("BATCH_MONGO_DATABASE_NAME"),
            collection_name=os.getenv("BATCH_MONGO_COLLECTION_NAME"),
        )
    )


# ========================================================================================


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

        response = self.client.delete_object(Bucket=self.BucketName, Key=Key,)
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


class AWSSQS(object):

    """Helper class to which add functionality on top of boto3 """

    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.sqs_client = boto3.resource(
            'sqs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def get_queue_by_name(self, queue_name=""):
        try:
            queue_name = self.sqs_client.get_queue_by_name(QueueName=queue_name)
            return queue_name
        except Exception as e:
            raise Exception("Error : {}".format(e))

    def __repr__(self):
        return "AWS SQS Helper class "


class Master(AWSS3, AWSSQS):

    def __init__(self):
        AWSS3.__init__(self,
                       aws_access_key_id=os.getenv("DEV_AWS_ACCESS_KEY"),
                       aws_secret_access_key=os.getenv("DEV_AWS_SECRET_KEY"),
                       region_name=os.getenv("DEV_AWS_REGION_NAME"),
                       bucket=os.getenv("S3_BUCKET"),
                       )
        AWSSQS.__init__(self,
                        aws_access_key_id=os.getenv("DEV_AWS_ACCESS_KEY"),
                        aws_secret_access_key=os.getenv("DEV_AWS_SECRET_KEY"),
                        region_name=os.getenv("DEV_AWS_REGION_NAME"),
                        )
        self.mongo_connector = Connector.MONGODB.value
        self.queue = self.get_queue_by_name(queue_name=os.getenv("QUEUE_NAME"))

    def run(self):
        response_step_1 = self.step_1_start_historical_data_dump()
        if response_step_1.get("status") == 200:
            print("Process complete ")
            return True
        else:
            return False

    def step_1_start_historical_data_dump(self):

        table_name = os.getenv("BATCH_MONGO_COLLECTION_NAME")
        key = "FileProcessedLogs/{}.json".format(table_name)

        """check key exist or not"""
        item_exist = self.item_exists(Key=key)
        print("item_exist", item_exist)

        if not item_exist:

            _data = bytes(json.dumps({"table_name": table_name,
                                      "last_created_date":datetime(2021, 3, 21, 0, 0, 0, tzinfo=timezone.utc).__str__(),
                                      "max_created_date":datetime(2022, 3, 21, 0, 0, 0, tzinfo=timezone.utc).__str__()}).encode("UTF-8"))
            self.put_files(Key=key, Response=_data)

        response = self.get_item(Key=key)
        first_created_date = parse(json.loads(response.decode("UTF-8")).get("last_created_date"))
        max_created_date = parse(json.loads(response.decode("UTF-8")).get("max_created_date"))


        """manually run for date range """
        # first_created_date = datetime(2021, 3, 22, 0, 0, 0, tzinfo=timezone.utc)
        # max_created_date = datetime(2021, 9, 23, 0, 0, 0, tzinfo=timezone.utc)
        print("Starting job......")
        print("first_created_date", first_created_date)
        print("max_created_date", max_created_date)


        while first_created_date < max_created_date:

            first_created_date = self.put_message_on_sqs(first_created_date, table_name, key, max_created_date)

            if first_created_date is not None:
                _data = bytes(json.dumps({"table_name": table_name,
                                          "last_created_date":first_created_date.__str__(),
                                          "max_created_date":max_created_date.__str__()}).encode("UTF-8"))
                self.put_files(
                    Key=key, Response=_data
                )

        if first_created_date is not None:
            return {"status": 200}
        else:
            return {"status": 412}

    def put_message_on_sqs(self, first_created_date, table_name, key, max_created_date):

        """Process messages on SQS Queue"""

        for hour in range(first_created_date.hour, 24):
            try:
                last_created_date = first_created_date + timedelta(hours=1)

                filter={
                    'createdAt': {
                        '$gte': first_created_date,
                        '$lt': last_created_date
                    }
                }

                count = self.mongo_connector.get_total_count(query=filter)

                flag = True

                if count > 0:
                    response_data = self.mongo_connector.get_data(query=filter)
                    while True:
                        try:
                            batch_data = next(response_data)
                            data = {"data":batch_data}

                            print("SENT TO SQS : {}".format(data))

                            response = self.queue.send_message(MessageBody=json.dumps(data, default=str))
                            print(response)

                        except StopIteration:
                            break
                        except Exception as e:
                            flag = False
                            break

                if flag:
                    first_created_date = last_created_date

                else:
                    raise Exception("Failed to process batch for {} date.".format(first_created_date))

            except Exception as e:
                print("_________{}___________".format(first_created_date))
                _data = bytes(json.dumps({"table_name": table_name,
                                          "last_created_date":first_created_date.__str__(),
                                          "max_created_date":max_created_date.__str__()}).encode("UTF-8"))
                self.put_files(
                    Key=key, Response=_data
                )
                first_created_date = None
                raise Exception("Failed to process further")

        return first_created_date


def main():
    helper  = Master()
    helper.run()


if __name__ == "__main__":
    main()
