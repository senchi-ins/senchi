import os
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from server.config import settings


def upload_file(file_name, bucket, object_name=None) -> bool:
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def upload_file_from_bytes(stream: bytes, bucket: str, object_name=None) -> bool:
    """Upload a file from a url to an S3 bucket
    """
    s3_client = boto3.client(
        's3',
        config=Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION),
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
        response = s3_client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=stream
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_file_url(bucket: str, object_name: str, expires_in: int = 3600) -> str:
    """Get a file url from an S3 bucket
    """
    s3_client = boto3.client(
        's3',
        config=Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION),
        region_name=settings.AWS_S3_REGION_NAME
    )
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': object_name},
        ExpiresIn=expires_in
    )


if __name__ == "__main__":
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    print(response)