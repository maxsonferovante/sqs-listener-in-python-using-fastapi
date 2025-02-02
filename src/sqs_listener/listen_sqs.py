import json
import boto3
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

def listen_sqs():
    try:
        logger.info("Listening to SQS - %s", os.getenv('QUEUE_URL'))
        sqs = boto3.client('sqs',
            endpoint_url=os.getenv('QUEUE_URL'),
            region_name= os.getenv('REGION_SQS'),
            aws_access_key_id= os.getenv('KEY_ACCESS'),
            aws_secret_access_key=os.getenv('KEY_SECRET'))
        response = sqs.receive_message(
            QueueUrl=os.getenv('QUEUE_URL'),
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        logger.info("Response from SQS: %s", response)
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            body = json.loads(message['Body'])
            logger.info("Received message: %s", body)
            sqs.delete_message(
                QueueUrl=os.getenv('QUEUE_URL'),
                ReceiptHandle=receipt_handle
            )        
    except Exception as e:
        logger.error("Error in listening to SQS - %s", e)


if __name__ == "__main__":
    listen_sqs()