A user uploads images to an AWS S3 bucket in a specified "folder" / "prefix".
An AWS Lambda function configured to get triggered on a PUT request to the S3 bucket invokes an AWS SQS.
The function appends the bucket and key to the SQS queue along with other metadata (such as the image resize size).
A queue consumer process running in a private subnet of the non-default VPC polls the queue for any images and resizes the images based on the data provided to it.

For this demonstration, the resize size and queue name are passed as parameters to the queue consumer ec2 instance.

This repository assists in creating AWS resoureces for demonstrating event-and-queue-based architecture components for the example discussed above.

There are three cloudformation stacks which need to be created before executing the demo:

* network-stack: network-resources.yml
** Resources: 
    *** One public subnet (web*) in each of 3 availability zones.
    *** Two private subnets (db* and app*) in each of 3 availability zones.
    *** One internet gateway
    *** Two non-Main route tables (one for public subnets and one for private subnets)
    *** One security group for allowing access to ports 22, 80 and 443

* natgw-stack: natgw-resources.yml
** Resources:
    *** One Natgateway with one elastic ipaddress in each availability zone.
    *** One route table each for two private subnets mapped to one Natgw in respective availability zones.

* launch-template-sqs-lambda-stack: launch-template-sqs-lambda.yml
** Resources:
    *** One launch template configured with the above security group and an IAM instance profile
    *** 

* AWS Lambda Function: An AWS lambda function configured to execute within private subnets in a non-default VPC gets triggered due to a PUT request on a AWS S3 bucket.

