from dotenv import load_dotenv
import os

load_dotenv('../.env')

def get_os():
    AWS_S3_BUCKET = os.getenv("MINIO_SILVER_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    ENDPOINT_OVERRIDE = os.getenv("MINIO_ENDPOINT_URL")

    return [AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ENDPOINT_OVERRIDE]