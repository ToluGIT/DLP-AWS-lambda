import json
import boto3
import logging
from botocore.exceptions import ClientError


s3 = boto3.client('s3')
sns = boto3.client('sns')

DESTINATION_BUCKET_NAME = 'encrydlp303'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:xxxxxxxx:dlp303'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event, indent=2)}")
    
    try:

        finding = event.get('detail', None)
        if not finding:
            raise KeyError("'detail' key not found in event.")


        bucket_arn = finding['resourcesAffected']['s3Object']['bucketArn']
        source_bucket = bucket_arn.split(":::")[1]
        object_key = finding['resourcesAffected']['s3Object']['key']
        severity = finding['severity']['description']
        
        logger.info(f"Sensitive data found in bucket {source_bucket}, file: {object_key} with severity {severity}")
        

        move_sensitive_file(source_bucket, object_key)
        
        message = (f"Sensitive data found and quarantined:\n"
                  f"Source Bucket: {source_bucket}\n"
                  f"File: {object_key}\n"
                  f"Severity: {severity}\n"
                  f"Moved to: {DESTINATION_BUCKET_NAME}")
        
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject='Sensitive Data Alert')
        logger.info("Remediation and notification completed successfully.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Sensitive Data Remediation Completed Successfully')
        }
        
    except KeyError as e:
        logger.error(f"Error in processing Macie finding: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing Macie finding: {str(e)}')
        }
    except ClientError as e:
        logger.error(f"AWS client error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'AWS Service Error: {str(e)}')
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}')
        }

def move_sensitive_file(source_bucket, object_key):
    """Move the sensitive file to another bucket."""
    try:
        s3.copy_object(
            Bucket=DESTINATION_BUCKET_NAME,
            Key=object_key,
            CopySource={'Bucket': source_bucket, 'Key': object_key}
        )
        logger.info(f"File {object_key} copied from bucket {source_bucket} to bucket {DESTINATION_BUCKET_NAME}.")
        
        s3.delete_object(
            Bucket=source_bucket,
            Key=object_key
        )
        logger.info(f"File {object_key} deleted from bucket {source_bucket}.")
        
    except ClientError as e:
        logger.error(f"Error moving file {object_key} from bucket {source_bucket}: {str(e)}")
        raise
