import os, re
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

upload_path = os.environ.get('UPLOAD_DIR_NAME')

# Helper function
def create_google_maps_url(gps_coords):
    # Exif data stores coordinates in degree/minutes/seconds format. To convert to decimal degrees.
    # We extract the data from the dictionary we sent to this function for latitudinal data.
    dec_deg_lat = convert_decimal_degrees(
        float(gps_coords["lat"][0]),
        float(gps_coords["lat"][1]),
        float(gps_coords["lat"][2]),
        gps_coords["lat_ref"],
    )
    # We extract the data from the dictionary we sent to this function for longitudinal data.
    dec_deg_lon = convert_decimal_degrees(
        float(gps_coords["lon"][0]),
        float(gps_coords["lon"][1]),
        float(gps_coords["lon"][2]),
        gps_coords["lon_ref"],
    )
    # We return a search string which can be used in Google Maps
    return f"https://maps.google.com/?q={dec_deg_lat},{dec_deg_lon}"


# Converting to decimal degrees for latitude and longitude is from degree/minutes/seconds format is the same for latitude and longitude. So we use DRY principles, and create a seperate function.
def convert_decimal_degrees(degree, minutes, seconds, direction):
    decimal_degrees = degree + minutes / 60 + seconds / 3600
    # A value of "S" for South or West will be multiplied by -1
    if direction == "S" or direction == "W":
        decimal_degrees *= -1
    return decimal_degrees

photo_format = ["jpg", "png", "jpeg", "bmp"]

def get_exif(file):
    exif_dict = {}
    if any(extension in file.lower() for extension in photo_format):
        gps_coords = {}
        _path = os.path.join(upload_path, file)
        image = Image.open(_path)
        exif_dict['type'] = 'photos'
        
        # 1-1. 사진에 metedata가 없을 때
        if image._getexif() == None:
            print(f"{file} contains no exif data.")
            # Strongly fix the datetime string type with regex
            pattern = r"202([0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])"
            match = re.search(pattern, file)
            if match:
                exif_dict['DateTime'] = match.group()
            elif file.startswith("16") or file.startswith("17"):
                unixtime = int(file[:10])
                exif_dict['DateTime'] = datetime.utcfromtimestamp(unixtime).strftime('%Y%m%d')
            else:
                print(f"{file} : (Photo)정규표현식 추출가능 문자열 없음")
        # 1-2. 사진에 metadata가 있을 때        
        else:
            pattern = r"202([0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])"
            match = re.search(pattern, file)
            for tag, value in image._getexif().items():
                tag_name = TAGS.get(tag)
                try:
                    # 1-3. 사진 metadata에 DateTime Key가 있을 때
                    if 'DateTime' in tag_name:
                        exif_dict['DateTime'] = value
                except Exception as e:
                    print(e)
            # 1-4. 사진 metadata에 DateTime Key가 없을 때
            if len(exif_dict) == 1:
                if match:
                    exif_dict['DateTime'] = match.group()
                elif file.startswith("16") or file.startswith("17"):
                    unixtime = int(file[:10])
                    exif_dict['DateTime'] = datetime.utcfromtimestamp(unixtime).strftime('%Y%m%d')
            
    # 2-1. 비디오 포맷일 때
    else:
        print("Video Format")
        exif_dict['type'] = 'video'
        pattern = r"202([0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])"
        match = re.search(pattern, file)
        # 2-2. 파일 이름에 YYYYMMDD 형식이 있을 때
        if match:
            exif_dict['DateTime'] = match.group()
        elif file.startswith("16") or file.startswith("17"):
            unixtime = int(file[:10])
            exif_dict['DateTime'] = datetime.utcfromtimestamp(unixtime).strftime('%Y%m%d')
        else:
            print(f"{file} : (Video)정규표현식 추출가능 문자열 없음")
    return exif_dict

if __name__ == "__main__":
    exif_dict = get_exif('1691364246262.jpg')
    print(exif_dict)