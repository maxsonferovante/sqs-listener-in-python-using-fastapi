import json
import boto3
import os
import logging


logger = logging.getLogger(__name__)


def listen_sqs():
    try:
        sqs = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
        logger.info("Listening to SQS - %s", os.environ['SQS_QUEUE_URL'])
        response = sqs.receive_message(
            QueueUrl=os.environ['SQS_QUEUE_URL'],
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if "Messages" in response:
            for message in response['Messages']:
                body = json.loads(message['Body'])
                message_receipt_handle = message['ReceiptHandle']
                
                logger.info("Message received: %s", body)
                logger.info("Message Receipt Handle: %s", message_receipt_handle)
                

                sqs.delete_message(
                    QueueUrl=os.environ['SQS_QUEUE_URL'],
                    ReceiptHandle=message_receipt_handle
                )
        else:
            logger.info("No messages in queue")
    except Exception as e:
        logger.error("Error in listening to SQS - %s", e)