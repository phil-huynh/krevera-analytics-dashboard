import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from app.services.s3_service import S3Service


@pytest.mark.s3
class TestS3Service:
    @pytest.fixture
    def mock_s3_client(self):
        with patch('boto3.client') as mock_client:
            mock_s3 = Mock()
            mock_client.return_value = mock_s3
            yield mock_s3

    @pytest.fixture
    def s3_service_instance(self, mock_s3_client):
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.S3_ENDPOINT_URL = "http://localhost:4566"
            mock_settings.AWS_ACCESS_KEY_ID = "test"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.S3_BUCKET_NAME = "test-bucket"

            mock_s3_client.head_bucket.return_value = {}

            service = S3Service()
            return service

    def test_upload_file_success(self, s3_service_instance, mock_s3_client):
        file_content = b"test content"
        object_key = "test/file.json"

        mock_s3_client.put_object.return_value = {}

        result = s3_service_instance.upload_file(file_content, object_key)

        assert result == f"s3://{s3_service_instance.bucket_name}/{object_key}"
        mock_s3_client.put_object.assert_called_once_with(
            Bucket=s3_service_instance.bucket_name,
            Key=object_key,
            Body=file_content
        )

    def test_upload_file_client_error(self, s3_service_instance, mock_s3_client):
        file_content = b"test content"
        object_key = "test/file.json"

        mock_s3_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "Bucket not found"}},
            "put_object"
        )

        with pytest.raises(ClientError):
            s3_service_instance.upload_file(file_content, object_key)

    def test_download_file_success(self, s3_service_instance, mock_s3_client):
        object_key = "test/file.json"
        expected_content = b"downloaded content"

        mock_response = {"Body": Mock()}
        mock_response["Body"].read.return_value = expected_content
        mock_s3_client.get_object.return_value = mock_response

        result = s3_service_instance.download_file(object_key)

        assert result == expected_content
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=s3_service_instance.bucket_name,
            Key=object_key
        )

    def test_download_file_not_found(self, s3_service_instance, mock_s3_client):
        object_key = "nonexistent/file.json"

        mock_s3_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}},
            "get_object"
        )

        with pytest.raises(ClientError):
            s3_service_instance.download_file(object_key)

    def test_file_exists_true(self, s3_service_instance, mock_s3_client):
        object_key = "test/file.json"

        mock_s3_client.head_object.return_value = {}

        result = s3_service_instance.file_exists(object_key)

        assert result is True
        mock_s3_client.head_object.assert_called_once_with(
            Bucket=s3_service_instance.bucket_name,
            Key=object_key
        )

    def test_file_exists_false(self, s3_service_instance, mock_s3_client):
        object_key = "nonexistent/file.json"

        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "head_object"
        )

        result = s3_service_instance.file_exists(object_key)

        assert result is False

    def test_file_exists_other_error(self, s3_service_instance, mock_s3_client):
        object_key = "test/file.json"

        mock_s3_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "Internal Error"}},
            "head_object"
        )

        with pytest.raises(ClientError):
            s3_service_instance.file_exists(object_key)

    def test_get_s3_uri(self, s3_service_instance):
        object_key = "datasets/test.json"

        result = s3_service_instance.get_s3_uri(object_key)

        assert result == f"s3://{s3_service_instance.bucket_name}/{object_key}"

    def test_bucket_creation_on_init(self, mock_s3_client):
        with patch('app.services.s3_service.settings') as mock_settings:
            mock_settings.S3_ENDPOINT_URL = "http://localhost:4566"
            mock_settings.AWS_ACCESS_KEY_ID = "test"
            mock_settings.AWS_SECRET_ACCESS_KEY = "test"
            mock_settings.AWS_REGION = "us-east-1"
            mock_settings.S3_BUCKET_NAME = "new-bucket"

            mock_s3_client.head_bucket.side_effect = ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}},
                "head_bucket"
            )
            mock_s3_client.create_bucket.return_value = {}

            service = S3Service()
            _ = service.s3_client

            mock_s3_client.create_bucket.assert_called_once_with(Bucket="new-bucket")