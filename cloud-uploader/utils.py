import os, subprocess
from dotenv import load_dotenv
import pexpect

load_dotenv()

aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("REGION_NAME")

def partition_path(key_path, date_value, file_name):
    _path = f"{key_path}/yyyy={date_value[:4]}/mm={date_value[4:6]}/dd={date_value[6:]}/{file_name}"
    return _path

def upload_image_to_s3(s3, file_path, bucket_name, key):
    try:
        s3.upload_file(file_path, bucket_name, key)
    except Exception as e:
        print("Error uploading file:", str(e))


def check_file_exists_in_s3(s3, bucket_name, file_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except:
        return False
    
def count_files_in_s3_directory(s3, bucket_name, prefix):
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' in response:
            file_count = len(response['Contents'])
            return file_count
        else:
            return 0
    except Exception as e:
        print(f"Error counting files: {e}")
        return -1    


def run_aws_cli_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except Exception as e:
        return str(e)
    
def chown_dir(_path):
    command = [f"sudo chown ubuntu {_path}", f"sudo chown :ubuntu {_path}"]
    for comm in command:
        child = pexpect.spawn(comm)
        child.sendline("")
        child.expect(pexpect.EOF)

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

