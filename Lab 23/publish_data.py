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
import pynamodb.attributes as at
import datetime
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import *

load_dotenv(".env")

faker = Faker()

class UserModel(Model):
    class Meta:
        table_name = 'myTable'
        aws_access_key_id = "XXX"
        aws_secret_access_key = "XXXX"

    email = UnicodeAttribute(null=True)
    first_name = UnicodeAttribute(range_key=True)
    last_name = UnicodeAttribute(hash_key=True)


def main():

    try:UserModel.create_table(billing_mode='PAY_PER_REQUEST')
    except Exception as e:pass
    sleep(2)


    average = []
    for i in range(1, 50):

        starttime = datetime.now()
        UserModel(email=faker.email(), first_name=faker.first_name(), last_name=faker.last_name()).save()
        endtime = datetime.now()

        delta = endtime-starttime

        elapsed_time = int((delta.seconds * 1000) + (delta.microseconds / 1000))

        average.append(elapsed_time)
        print("Exection Time: {} MS ".format(elapsed_time))

    averagetime = sum(average)/ len(average)
    print("\nAverage Time in MS: {} ".format(averagetime))


main()
