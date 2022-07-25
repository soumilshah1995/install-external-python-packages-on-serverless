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


my_stream_name = "XXXXXXXXXXXXXXXXXXXXXXX"
print("Stream Name :{} ".format(my_stream_name))


kinesis_client = boto3.client('firehose',
                              region_name='us-east-1',
                              aws_access_key_id="XXXXXXXXXX",
                              aws_secret_access_key="XXXXXXXXXXXXXXXXXXXXXXXXE"
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
        DeliveryStreamName=my_stream_name,
        Record={
            'Data': json.dumps(json_data)
        }

    )
    print(put_response)




