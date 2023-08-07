import boto3, os
from dotenv import load_dotenv


load_dotenv()

aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("REGION_NAME")

def partition_path(key_path, date_value, file_name):
    _path = f"{key_path}/yyyy={date_value[:4]}/mm={date_value[4:6]}/dd={date_value[6:]}/{file_name}"
    return _path


def upload_image_to_s3(file_path, bucket_name, key):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    try:
        s3_client.upload_file(file_path, bucket_name, key)
    except Exception as e:
        print("Error uploading file:", str(e))


def check_file_exists_in_s3(bucket_name, file_key):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
    )
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except:
        return False


def get_size(start_path):
    total_size = 0
    fin = ""
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    if total_size == 0:
        return "Directory is empty"
    size_suffixes = ["B", "KB", "MB", "GB", "TB"]
    size_suffix_index = 0
    while total_size > 1024 and size_suffix_index < len(size_suffixes) - 1:
        total_size /= 1024
        size_suffix_index += 1
    return "{:.2f} {}".format(total_size, size_suffixes[size_suffix_index])

