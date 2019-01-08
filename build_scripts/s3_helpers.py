# Useful shortcuts for working with S3
import boto3
import botocore
import os
from urllib.parse import urlparse

def s3copy(src, dest):
    """Copies a file to or from s3"""
    s3 = boto3.client('s3', verify=False)
    if src.startswith("s3"):
        url_parsed = urlparse(src)
        print(url_parsed.netloc)
        print(url_parsed.path)
        s3.download_file(url_parsed.netloc, url_parsed.path[1:], dest)
    if dest.startswith("s3"):
        url_parsed = urlparse(dest)
        s3.upload_file(src, url_parsed.netloc, url_parsed.path)
