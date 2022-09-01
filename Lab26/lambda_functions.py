try:
    import boto3
    import csv
    import uuid
    import json
    import datetime
    import re
    from datetime import datetime
    import os
    import io
    from io import StringIO
    from dotenv import load_dotenv
    load_dotenv(".env")

except Exception as e:
    print("Error :{} ".format(e))


class AWSS3(object):
    """Helper class to which add functionality on top of boto3 """

    def __init__(
            self,
            bucket=os.getenv("REPORTS_BUCKETS"),
            aws_access_key_id=os.getenv("DEV_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("DEV_SECRET_KEY"),
            region_name=os.getenv("DEV_REGION"),
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
        response = self.client.delete_object(Bucket=self.BucketName, Key=Key)
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


def flatten_dict(data, parent_key="", sep="_"):
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


def create_workgroup_history(day, workgroup):
    print("**", day)
    file_name = "workgroup_{}_{}_queries.json".format(workgroup, day)

    records = ""

    athena = boto3.client(
        "athena",
        aws_access_key_id=os.getenv("DEV_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("DEV_SECRET_KEY"),
        region_name=os.getenv("DEV_REGION"),
    )

    paginator = athena.get_paginator("list_query_executions").paginate(
        WorkGroup=workgroup
    )
    print("paginator",paginator)

    for page in paginator:
        print("page", page)

        query_executions = athena.batch_get_query_execution(
            QueryExecutionIds=page["QueryExecutionIds"]
        )

        for query in query_executions["QueryExecutions"]:

            if "CompletionDateTime" not in query["Status"]:
                continue

            query_day = query["Status"]["CompletionDateTime"].strftime("%Y-%m-%d")
            print("query_day", query_day, type(query_day))
            print("day", day, type(day))

            if day == query_day:

                json_payload = {}

                json_payload["QueryExecutionId"] = query.get("QueryExecutionId")
                json_payload["Query"] = query.get("Query")
                json_payload["StatementType"] = query.get("StatementType")
                json_payload["WorkGroup"] = query.get("WorkGroup")

                for key, value in flatten_dict(
                        query.get("ResultConfiguration")
                ).items():
                    json_payload[key] = value.__str__()

                for key, value in flatten_dict(
                        query.get("QueryExecutionContext")
                ).items():
                    json_payload[key] = value.__str__()

                for key, value in flatten_dict(query.get("EngineVersion")).items():
                    json_payload[key] = value.__str__()

                for key, value in flatten_dict(query.get("Statistics")).items():
                    json_payload[key] = value.__str__()

                for key, value in flatten_dict(query.get("Status")).items():
                    json_payload[key] = value.__str__()

                for key, value in flatten_dict(query.get("Statistics")).items():
                    json_payload[key] = value.__str__()

                records = records + json.dumps(json_payload) + "\n"

            elif query_day < day:
                return records

    return records


def handler(event=None, context=None):

    current_day = datetime.now().strftime("%Y-%m-%d").__str__()
    report_date  = current_day

    workgroups = ["soumil"]

    for workgroup in workgroups:

        csv_buffer = StringIO()
        year, month, day = Datetime.get_year_month_day()
        file_name = "workgroup_{}_{}_queries.json".format(workgroup, report_date)

        response = create_workgroup_history(day=report_date, workgroup=workgroup)
        csv_buffer.write(response)
        csv_buffer.seek(0)

        helper = AWSS3()

        path = "{}/year={}/month={}/day={}/{}".format(
            os.getenv("S3AthenaReports"),
            year, month, day, file_name)

        helper.put_files(Response=csv_buffer.getvalue(), Key=path)

