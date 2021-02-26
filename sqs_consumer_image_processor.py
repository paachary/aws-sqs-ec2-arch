import os
from io import BytesIO
from signal import signal, SIGINT, SIGTERM

import PIL
import boto3
from PIL import Image

sqs_resource = boto3.resource('sqs')
sqs_client = boto3.client('sqs')
QUEUE_NAME = os.getenv("QUEUE_NAME")
IMAGE_SIZE = os.getenv("IMAGE_SIZE")


class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


def get_queue():
    """ Retrieve the SQS queue url from the queue name"""
    return sqs_resource.get_queue_by_name(QueueName=QUEUE_NAME)


def get_queue_url():
    return sqs_client.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')


def read_from_queue_single_msg():
    """Reading the queue for the s3 bucket and key names"""

    receive_message_result = sqs_client.receive_message(
        QueueUrl=get_queue_url(),
        MessageAttributeNames=["All"])

    bucket = receive_message_result['Messages'][0]['MessageAttributes']['S3Bucket']['StringValue']
    key = receive_message_result['Messages'][0]['MessageAttributes']['S3Key']['StringValue']
    print(" bucket is {} and key = {}".format(bucket, key))

    resize_image(bucket, key, IMAGE_SIZE)


def resize_image(bucket_name, key, size):
    size_split = size.split('x')
    s3 = boto3.resource('s3')
    obj = s3.Object(
        bucket_name=bucket_name,
        key=key
    )
    object_body = obj.get()['Body'].read()

    img = Image.open(BytesIO(object_body))
    img = img.resize((int(size_split[0]), int(size_split[1])), PIL.Image.ANTIALIAS)
    buffer = BytesIO()

    img.save(buffer, 'JPEG')
    buffer.seek(0)

    resized_key = "{size}_{key}".format(size=size, key=key)
    obj = s3.Object(bucket_name=bucket_name,
                    key=resized_key)
    obj.put(Body=buffer, ContentType='image/jpeg')

    print(f'uploaded the resized image to S3 bucket {bucket_name}')


def process_message(message_body):
    bucket = message.message_attributes.get('S3Bucket').get('StringValue')
    key = message.message_attributes.get('S3Key').get('StringValue')
    print(" bucket is {} and key = {}".format(bucket, key))
    resize_image(bucket, key, IMAGE_SIZE)


if __name__ == '__main__':
    print('entering the main function')
    # read_from_queue_single_msg()

    signal_handler = SignalHandler()
    while not signal_handler.received_signal:
        messages = get_queue().receive_messages(MessageAttributeNames=["All"], MaxNumberOfMessages=10,
                                                WaitTimeSeconds=1)
        for message in messages:
            try:
                process_message(message)
            except Exception as e:
                print(f"exception while processing message: {repr(e)}")
                continue

            message.delete()
