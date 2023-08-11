import os, boto3, time, shutil
import flet as ft
from flet_route import Params, Basket
from dotenv import load_dotenv
from utils import (run_aws_cli_command, 
                   check_file_exists_in_s3, 
                   count_files_in_s3_directory,
                   chown_dir)

load_dotenv()
##### GLOBAL VARIABLES #####
log_file = os.environ.get('LOGFILE_DIR_NAME')
upload_path = os.environ.get('UPLOAD_DIR_NAME')
download_path = os.environ.get("DOWNLOAD_DIR_NAME")
bucket_name = os.environ.get('S3_BUCKET_NAME')
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("REGION_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region,
)


def galleryPageView(page: ft.Page, params: Params, basket: Basket):
    page.bgcolor = ft.colors.BLACK45
    page.scroll = "always"
    page.controls.clear()
    
    def snackBar(msg, color, font_size, dur):
        page.snack_bar = ft.SnackBar(
                ft.Text(msg, size=font_size, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                duration=dur,
                )
        page.snack_bar.open = True
        page.update()
        
    def to_home(e):
        page.go("/")
        

    def download_image(prefix):
        command = f"aws s3 sync s3://{bucket_name}/photos/{prefix} {download_path}"
        run_aws_cli_command(command)
    
    grid_images = ft.GridView(
        height=400,
        width=ft.WindowDragArea,
        runs_count=5,
        max_extent=150,
        child_aspect_ratio=1.0,
        spacing=5,
        run_spacing=5,
    )
    
    def show_images(e):
        shutil.rmtree(download_path)
        os.mkdir(download_path)
        chown_dir(download_path)
        try:
            grid_images.controls.clear()
            page.controls.remove(grid_images)
            page.update()
        except: pass
        date_prefix = f"yyyy={year_.value}/mm={str(month_.value).zfill(2)}/dd={str(day_.value).zfill(2)}"
        
        pre = f'photos/{date_prefix}'
        
        if not os.listdir(download_path):
            download_image(date_prefix)
        else: pass
        
        
        while True:
            cnt = count_files_in_s3_directory(s3_client, bucket_name, pre)
            if len(os.listdir(download_path)) == cnt:
                break
        
        file_text.value = f"Photo Count : {cnt}"
        page.controls.insert(2, file_text)
        pic_list = os.listdir(download_path)
        
        for i in pic_list:
            grid_images.controls.append(
                ft.Image(
                    src=os.path.join('/s3-files', i),
                    fit=ft.ImageFit.CONTAIN,
                    repeat=ft.ImageRepeat.NO_REPEAT,
                    border_radius=ft.border_radius.all(10),
                )
            )
        page.controls.insert(3, grid_images)
        page.update()        

    def refresh_images(e):
        try:
            grid_images.controls.clear()
            page.controls.remove(grid_images)
            page.update()
        except: pass
        shutil.rmtree(download_path)
        os.mkdir(download_path)
        chown_dir(download_path)
        snackBar(
                f"Refreshed!"
                , 'GREY'
                , 16
                , 3000
                )
        
    show_image_btn = ft.ElevatedButton(
                content=ft.Icon(ft.icons.PHOTO),
                bgcolor=ft.colors.GREY_300,
                disabled=False,
                on_click=show_images
            )
    
    del_image_btn = ft.ElevatedButton(
        content=ft.Icon(ft.icons.REFRESH),
        bgcolor=ft.colors.GREY_300,
        disabled=False,
        on_click=refresh_images
    )
    
    file_text = ft.Text(style=ft.TextThemeStyle.BODY_MEDIUM)
    
    year_ = ft.TextField(label="년",
                         keyboard_type='NUMBER',
                         color='BLACK',
                         width=60,
                         height=30,
                         text_size=12)
    month_ = ft.TextField(label="월",
                         keyboard_type='NUMBER',
                         color='BLACK',
                         width=60,
                         height=30,
                         text_size=12)
    day_ = ft.TextField(label="일",
                         keyboard_type='NUMBER',
                         color='BLACK',
                         width=60,
                         height=30,
                         text_size=12)
    
    
    datetime_row = ft.Row(
        controls=[year_, month_, day_],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    upload_btn_row = ft.Row(
        controls=[show_image_btn, datetime_row, del_image_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    home_btn = ft.ElevatedButton(
                        "Go to HOME"
                        , on_click=to_home
                    )

    page.add(
        ft.AppBar(
                leading=ft.Icon(ft.icons.PHOTO),
                title=ft.Text("Family Gallery!"),
                bgcolor=ft.colors.SURFACE_VARIANT,
                ),
                upload_btn_row,
                home_btn
    )
    
    return ft.View(
                    "/gallery",
                    page.controls
                )