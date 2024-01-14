from dotenv import load_dotenv
import os, boto3

load_dotenv()

aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("REGION_NAME")


class S3_Functions:
    
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    
    subfolder_list = []
    def __init__(self, bucket_name, prefix, local_filepath):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.local_filepath = local_filepath
        
    def upload_image_to_s3(s3, local_filepath, bucket_name, prefix):
        try:
            s3.upload_file(local_filepath, bucket_name, prefix)
        except Exception as e:
            print("Error uploading file:", str(e))