import boto3 ## PACKAGE TO INTERACT WITH AWS S3 
from botocore.exceptions import NoCredentialsError  ## ERROR HANDLING 
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv() 

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

def upload_to_s3(file_path, bucket_name, s3_file_name):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_file_name)
        return f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_file_name}"
    except FileNotFoundError:
        return "File not found"
    except NoCredentialsError:
        return "Credentials not available"

def download_from_s3(bucket_name, s3_file_name, local_file_name):
    try:
        s3_client.download_file(bucket_name, s3_file_name, local_file_name)
        return True
    except NoCredentialsError:
        return False