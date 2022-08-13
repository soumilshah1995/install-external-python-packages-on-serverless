import json
import logging
import os
import boto3

def consume(event, context):
    print(event)
    return 200
