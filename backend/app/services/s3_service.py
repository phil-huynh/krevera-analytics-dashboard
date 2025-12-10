import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self._s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME

    @property
    def s3_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self._ensure_bucket_exists()
        return self._s3_client

    def _ensure_bucket_exists(self) -> None:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket '{self.bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Creating S3 bucket '{self.bucket_name}'")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                raise

    def upload_file(self, file_content: bytes, object_key: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content
            )
            s3_uri = f"s3://{self.bucket_name}/{object_key}"
            logger.info(f"Uploaded file to {s3_uri}")
            return s3_uri
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise

    def download_file(self, object_key: str) -> bytes:
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            content = response['Body'].read()
            logger.info(f"Downloaded file from s3://{self.bucket_name}/{object_key}")
            return content
        except ClientError as e:
            logger.error(f"Failed to download from S3: {e}")
            raise

    def file_exists(self, object_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def get_s3_uri(self, object_key: str) -> str:
        return f"s3://{self.bucket_name}/{object_key}"


s3_service = S3Service()