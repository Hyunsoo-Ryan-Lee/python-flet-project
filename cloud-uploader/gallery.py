import os, boto3, re, shutil
import flet as ft
from flet_route import Params, Basket
from dotenv import load_dotenv
from utils import (run_aws_cli_command, 
                   get_subfolders_in_bucket, 
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
    
    date_dict = {}
    
    _, list_ = get_subfolders_in_bucket(s3_client, bucket_name, 'photos/', [])

    for p in list_:
        dd = [i for i in re.split('photos|yyyy=|mm=|dd=|/', p) if i]
        if dd[0] not in date_dict:
            date_dict[dd[0]] = {}

        if dd[1] not in date_dict[dd[0]]:
            date_dict[dd[0]][dd[1]] = []
        
        if dd[2] not in date_dict[dd[0]][dd[1]]:
            date_dict[dd[0]][dd[1]].append(dd[2])     
    
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
    
    def animate_container(e):
        pass
        # file_text.value  = grid_images.controls[0]
        # file_text.update()
        # grid_images.controls[0].width = 100
        # grid_images.controls[0].height = 100
        # grid_images.controls[0].update()
    
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
                ft.Container(
                    animate=ft.animation.Animation(300, 'easeInOut'),
                    content=
                        ft.Image(
                            src=os.path.join('/s3-files', i),
                            fit=ft.ImageFit.CONTAIN,
                            repeat=ft.ImageRepeat.NO_REPEAT,
                            border_radius=ft.border_radius.all(10),
                        ),
                    # on_click=animate_container
            )
            )
        page.controls.insert(3, grid_images)
        page.update()        

    def refresh_images(e):
        try:
            grid_images.controls.clear()
            page.controls.remove(grid_images)
            file_text.value = ""
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
    
    def monthly_(e):
        try:
            month_.options.clear()
            m_list = list(date_dict[year_.value].keys())
        except: 
            m_list = []
        for m in m_list:
            month_.options.append(ft.dropdown.Option(m))
        page.update()

    def daily_(e):
        try:
            day_.options.clear()
            d_list = date_dict[year_.value][month_.value]
        except: 
            d_list = []
        for d in d_list:
            day_.options.append(ft.dropdown.Option(d))
        page.update()
    
    y_list = list(date_dict.keys())
    
    year_ = ft.Dropdown(
        width=60,
        # height=40,
        options=[
            ft.dropdown.Option(i) for i in y_list
        ],
        on_focus=monthly_
    )
    
    month_ = ft.Dropdown(
        width=60,
        options=[],
        on_focus=daily_
    )

    day_ = ft.Dropdown(
        width=60,
        options=[],
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
    
    datetime_row = ft.Row(
        controls=[year_,month_,day_],
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
                    page.controls,
                    scroll='always'
                )