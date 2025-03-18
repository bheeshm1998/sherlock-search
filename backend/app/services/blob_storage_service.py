import boto3
import os
from botocore.exceptions import NoCredentialsError

# Get S3 credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION
)

def upload_to_s3(file_path: str, file_name: str) -> str:
    """
    Uploads a file to S3 and returns the file URL.
    """
    try:
        s3_client.upload_file(file_path, AWS_S3_BUCKET_NAME, file_name)
        file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{file_name}"
        return file_url
    except NoCredentialsError:
        raise Exception("S3 credentials not found. Check environment variables.")
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")