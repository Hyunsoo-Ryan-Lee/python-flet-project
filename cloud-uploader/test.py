import boto3, os, re
from dotenv import load_dotenv
from exif_info import get_exif
from utils import partition_path, count_files_in_s3_directory, upload_image_to_s3, check_file_exists_in_s3
import subprocess


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

def one_subfolders_in_bucket(bucket_name, prefix=''):
    s3 = boto3.client('s3')
    subfolders = []

    # List objects in the bucket using the specified prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')

    # Add subfolders to the list
    if 'CommonPrefixes' in response:
        subfolders.extend([obj['Prefix'] for obj in response['CommonPrefixes']])

    return subfolders



def get_subfolders_in_bucket(s3, bucket_name, prefix, dir_list):

    while True:
        subfolders = []
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')

        if 'CommonPrefixes' in response:
            subfolders.extend([obj['Prefix'] for obj in response['CommonPrefixes']])
            for sub in subfolders:
                folder, dir_list = get_subfolders_in_bucket(s3, bucket_name, sub, dir_list)
                aa = 0
                if not folder:
                    aa += 1
                    dir_list.append(sub)
                if len(folder) == aa:
                    break
        return subfolders, dir_list


def run_aws_cli_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # yy = '2021'
    # mm = '07'
    # for i in range(1,32):
    #     pre = f'photos/yyyy={yy}/mm={mm}/dd={str(i).zfill(2)}'
    #     cnt = count_files_in_s3_directory(s3_client, bucket_name, pre)
    #     print(yy,mm,i, '----',cnt)
        
    # bucket_name = bucket_name
    # remote_path = "photos/yyyy=2023/mm=08/dd=071691374359908.jpg"
    # local_path = "/home/ubuntu/Flet-App/python-flet-project/cloud-uploader/s3-files"
    # download_s3_file(s3_client, bucket_name, remote_path, local_path)
    y_, m_, d_ = [],[],[]
    prefix = 'photos/'  # Optional: Set the prefix to filter subfolders
    dir_list = []
    
    subfolders, list_ = get_subfolders_in_bucket(s3_client, bucket_name, prefix, dir_list)
    
    date_dict = {}
    for p in list_:
        dd = [i for i in re.split('photos|yyyy=|mm=|dd=|/', p) if i]
        if dd[0] not in date_dict:
            date_dict[dd[0]] = {}
        
        if dd[1] not in date_dict[dd[0]]:
            date_dict[dd[0]][dd[1]] = []
        
        if dd[2] not in date_dict[dd[0]][dd[1]]:
            date_dict[dd[0]][dd[1]].append(dd[2])
    
    print(date_dict)
    
    # file = "image.jpg"
    # exif_data = get_exif(file)
    # print(exif_data)
    # s3_subdir = exif_data.get("type", "noType")
    # _datetime = exif_data.get("DateTime", "")
    # _datetime = _datetime.replace(" ", "")
    # _datetime = _datetime.replace(":", "")[:8]
    # _path = os.path.join(upload_path, file)
    # s3_key = partition_path(s3_subdir, _datetime, file)
    # print(s3_key)
    # print(check_file_exists_in_s3(s3_client, bucket_name, s3_key))