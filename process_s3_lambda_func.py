import os

import boto3

QUEUE_NAME = os.getenv("QUEUE_NAME")
SQS = boto3.client("sqs")


def get_queue_url():
    """ Retrieve the SQS queue url from the queue name"""
    return SQS.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')


def lambda_handler(event, context):
    """The lambda Handler"""
    """Fetch the bucket and the key from the event"""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        print("key = {}".format(key))

        response = SQS.send_message(
            QueueUrl=get_queue_url(),
            MessageBody='s3-file',
            MessageAttributes={
                'S3Bucket': {
                    'StringValue': bucket,
                    'DataType': 'String'
                },
                'S3Key': {
                    'StringValue': key,
                    'DataType': 'String'
                }
            })

        print(f'Response is {response}')
