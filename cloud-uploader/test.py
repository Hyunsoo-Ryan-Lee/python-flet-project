import boto3, os
from dotenv import load_dotenv
from exif_info import get_exif
from utils import partition_path, upload_image_to_s3, check_file_exists_in_s3
import pexpect
import time


load_dotenv()
##### GLOBAL VARIABLES #####
log_file = os.environ.get('LOGFILE_DIR_NAME')
upload_path = os.environ.get('UPLOAD_DIR_NAME')
bucket_name = os.environ.get('S3_BUCKET_NAME')
aws_key = os.environ.get("AWS_KEY")
aws_passwd = os.environ.get("AWS_PASSWD")
s3_client = boto3.client('s3',
                    aws_access_key_id = aws_key,
                    aws_secret_access_key = aws_passwd,
                    region_name = "ap-northeast-2"
                    )

# def upload_image_to_s3(s3_client, file_path, bucket_name, key):
#     try:
#         s3_client.upload_file(file_path, bucket_name, key)
#     except Exception as e:
#         print("Error uploading file:", str(e))

if __name__ == "__main__":
    file = "image.jpg"
    exif_data = get_exif(file)
    print(exif_data)
    s3_subdir = exif_data.get("type", "noType")
    _datetime = exif_data.get("DateTime", "")
    _datetime = _datetime.replace(" ", "")
    _datetime = _datetime.replace(":", "")[:8]
    _path = os.path.join(upload_path, file)
    s3_key = partition_path(s3_subdir, _datetime, file)
    print(s3_key)
    # upload_image_to_s3(s3_client, _path, bucket_name, s3_key)
    print(check_file_exists_in_s3(s3_client, bucket_name, s3_key))