import time

import boto3
from faker import Faker
import json
from dotenv import load_dotenv
load_dotenv(".env")
import os

try:
    from dotenv import load_dotenv
    load_dotenv(".env")

    os.environ['AWS_ACCESS_KEY_ID'] = os.getenv("DEV_ACCESS_KEY")
    os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv("DEV_SECRET_KEY")
    os.environ['AWS_REGION'] = os.getenv("DEV_REGION")
except Exception as e:
    print("Error",e)


# Create a Faker object
fake = Faker()

# Define the SQS queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/043916019468/data-ingestion-queue'

# Create an SQS client
sqs = boto3.client('sqs')

# Generate fake data and publish to SQS
while True:
    # Generate fake data
    fake_data = {
        'name': fake.name(),
        'address': fake.address(),
        'phone_number': fake.phone_number()
    }

    # Convert the fake data to a JSON string
    message_body = json.dumps(fake_data)

    # Publish the message to the SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )

    print(f"Message ID: {response['MessageId']}")
    print(f"Message Contents: {message_body}")

