import tempfile
from typing import Optional

import boto3

from pysubs.utils.constants import EnvConstants
from pysubs.exceptions.awss3 import S3InvalidUploadSource
from pysubs.utils.settings import PySubsSettings


class AwsS3:
    def __init__(self) -> None:
        s3 = boto3.resource('s3')
        bucket_name = PySubsSettings.get_config(EnvConstants.AWS_S3_BUCKET)
        self.bucket = s3.Bucket(bucket_name)

    def __repr__(self):
        return f"AWS S3 Class Instance with Bucket Set to {self.bucket}"

    def download_object(self, file_url: str) -> str:
        """
        Downloads an object from AWS S3 and returns the content of the file in either str or bytes format
        :param file_url:
        :return:
        """
        with tempfile.NamedTemporaryFile(mode="w+b") as tmpFile:
            content = self.bucket.download_fileobj(file_url, tmpFile)
            tmpFile.write(content)
            tmpFile.seek(0)
            content = tmpFile.read()
        return content

    def upload_object(
            self,
            s3_filename: str,
            file_content: Optional[bytes] = None,
            file_path: Optional[str] = None
    ) -> None:
        """
        Uploads file content directly or the content of the file from the given path to
        AWS S3 with the specified file name.
        :param s3_filename:
        :param file_content:
        :param file_path:
        :return:
        """
        if file_content:
            with tempfile.TemporaryFile() as tmpFile:
                tmpFile.write(file_content)
                tmpFile.seek(0)
                self.bucket.upload_fileobj(tmpFile)
        elif file_path:
            self.bucket.upload_file(file_path, s3_filename)
        else:
            raise S3InvalidUploadSource("Both file_content and file_path cannot be empty.")
