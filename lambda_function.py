import boto3
import logging
import os
from botocore.exceptions import ClientError

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Configuration
SOURCE_BUCKET_NAME = 'sensitivebuck303'
DESTINATION_BUCKET_NAME = 'encrytomac303'
# SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:xxxxxxxxx:deployment-complete'

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Print the full event to the logs for debugging
    logger.info(f"Received event: {event}")

    try:
        # Extracting the 'detail' field from the event
        finding = event.get('detail', None)
        if not finding:
            raise KeyError("'detail' key not found in event.")

        object_key = finding['resourcesAffected']['s3Object']['key']
        severity = finding['severity']['description']

        logger.info(f"Sensitive data found in: {object_key} with severity {severity}")

        # Remediate by moving the sensitive file to another bucket
        move_sensitive_file(object_key)

        # Send SNS notification
        # message = f"Sensitive data found and moved to {DESTINATION_BUCKET_NAME}: {object_key}. Severity: {severity}"
        # sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject='Sensitive Data Alert')

        logger.info("Remediation and notification completed successfully.")
    except KeyError as e:
        logger.error(f"Error in processing Macie finding: {str(e)}")
        raise
    except ClientError as e:
        logger.error(f"AWS client error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

def move_sensitive_file(object_key):
    """Move the sensitive file to another bucket."""
    try:
        # Copy the object to the destination bucket
        s3.copy_object(
            Bucket=DESTINATION_BUCKET_NAME,
            Key=object_key,
            CopySource={'Bucket': SOURCE_BUCKET_NAME, 'Key': object_key}
        )
        logger.info(f"File {object_key} copied to bucket {DESTINATION_BUCKET_NAME}.")

        # Delete the object from the source bucket
        s3.delete_object(
            Bucket=SOURCE_BUCKET_NAME,
            Key=object_key
        )
        logger.info(f"File {object_key} deleted from bucket {SOURCE_BUCKET_NAME}.")
    except ClientError as e:
        logger.error(f"Error moving file {object_key}: {str(e)}")
        raise
