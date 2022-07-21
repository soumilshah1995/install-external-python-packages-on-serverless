import boto3
import json
from datetime import datetime
import calendar
import random
import time
import json
from faker import Faker
import uuid
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv(".env")


my_stream_name = os.getenv("StreamName")
print("Stream Name :{} ".format(my_stream_name))


kinesis_client = boto3.client('kinesis',
                              region_name='us-east-1',
                              aws_access_key_id=os.getenv("my_aws_access_key_id"),
                              aws_secret_access_key=os.getenv("my_aws_secret_access_key")
                              )
faker = Faker()


for i in range(1, 10):
    json_data = {
        "name":faker.name(),
        "city":faker.city(),
        "phone":faker.phone_number(),
        "id":uuid.uuid4().__str__(),
        "customer_id":random.randint(1,5)
    }
    print(json_data)
    sleep(0.5)

    put_response = kinesis_client.put_record(
        StreamName=my_stream_name,
        Data=json.dumps(json_data),
        PartitionKey='name')
    print(put_response)




