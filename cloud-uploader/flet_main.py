from typing import Dict
import flet as ft
import os, time, shutil, boto3
import pexpect
from datetime import datetime, timezone, timedelta
from time import localtime
from dotenv import load_dotenv
from exif_info import get_exif
from utils import partition_path, upload_image_to_s3, get_size, check_file_exists_in_s3


load_dotenv()
##### GLOBAL VARIABLES #####
log_file = os.environ.get('LOGFILE_DIR_NAME')
upload_path = os.environ.get('UPLOAD_DIR_NAME')
bucket_name = os.environ.get('S3_BUCKET_NAME')

##### MAIN CODE #####
def main(page: ft.Page):
    prog_bars: Dict[str, ft.ProgressRing] = {}
    files = ft.Ref[ft.Column]()
    upload_button = ft.Ref[ft.ElevatedButton]()
    page.title = "Photo Uploader"
    page.bgcolor = ft.colors.WHITE
    page.scroll = "always"
    
    
    def snackBar(msg, color, font_size, dur):
        page.snack_bar = ft.SnackBar(
                ft.Text(msg, size=font_size, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                duration=dur,
                )
        page.snack_bar.open = True
        page.update()

    def chown_dir():
        command = [f"sudo chown ubuntu {upload_path}", f"sudo chown :ubuntu {upload_path}"]
        for comm in command:
            child = pexpect.spawn(comm)
            child.sendline("")
            child.expect(pexpect.EOF)

    def file_picker_result(e: ft.FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ft.ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(ft.Row([prog, ft.Text(f.name)]))
        page.update()

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = ft.FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        start = time.time()
        KST = timezone(timedelta(hours=9))
        time_record = datetime.now(KST).strftime('%Y%m%d')
        time_stamp = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
        _y = time_record[:4]
        _m = time_record[4:6]
        _d = time_record[6:]
        uf = []
        if file_picker.result is not None and file_picker.result.files is not None:
            for f in file_picker.result.files:
                uf.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=page.get_upload_url(f.name, 600),
                    )
                )
            file_picker.upload(uf)
        # File이 Upload 다 되었는지 확인
        while True:
            if len(os.listdir(upload_path)) == len(uf):
                break
        time.sleep(1)
        
        total_file_count = len(os.listdir(upload_path))
        total_file_size = get_size(upload_path)
        
        log_txt = time_stamp + "\n"
        s3_file_path = []
        # File Upload 확인 후 Meta 추출 및 datetime에 따른 partition 생성 후 S3 Upload
        for i, file in enumerate(os.listdir(upload_path)):
            exif_data = get_exif(file)
            s3_subdir = exif_data.get('type', 'noType')
            _datetime = exif_data.get('DateTime', '')
            _datetime = _datetime.replace(' ', '')
            if _datetime:
                _datetime = _datetime.replace(':', '')[:8]
                s3_key = partition_path(s3_subdir, _datetime, file)
            else:
                # image meta 혹은 file name에서 datetime 형식 추출 안되었을 때는 
                # UnidentifiedDate 경로 하위에 오늘 날짜로 partition 잡혀서 이행
                s3_key = f"UnidentifiedDate/yyyy={_y}/mm={_m}/dd={_d}/{file}"
            log_txt += (s3_key + "\n")
            s3_file_path.append(s3_key)
            _path = os.path.join(upload_path, file)
            upload_image_to_s3(_path, bucket_name, s3_key)
        
        is_uploaded = []
        for s3_key in s3_file_path:
            if check_file_exists_in_s3(bucket_name, s3_key):
                is_uploaded.append(True)
            else:
                is_uploaded.append(False)
        
        time.sleep(0.5)
        if is_uploaded.count(True) == total_file_count:
            
            log_txt += "\n"
            with open(log_file, 'a') as file:
                file.write(log_txt)
            
            visual_log_txt = log_txt.replace(time_stamp+'\n','').replace('\n', '\n\n')
            
            tot = localtime(time.time()-start)
            time.sleep(1)
            snackBar(
                    f"{total_file_count} files Have been Successfully uploaded to AWS Cloud"
                    , 'GREEN'
                    , 16
                    , 3000
                    )
            # S3 Upload 후 디렉토리 비움
            open_dlg()
            upload_info_text.value = f"""
            \tUPLOADED FILE COUNT : {total_file_count}\n
            \tUPLOADED FILE SIZE : {total_file_size}\n
            \tUPLOADED TIME : {tot.tm_min} 분 {tot.tm_sec} 초\n
            \tUPLOAD PATH\n
            {visual_log_txt}
            """
            init_page()
            files.current.controls.insert(1, upload_info_text)
            page.update()
            time.sleep(4)
            shutil.rmtree(upload_path)
            os.mkdir(upload_path)
            chown_dir()
        else:
            snackBar(
                    f"Files Has Not Been Uploaded Properly"
                    , 'GREY'
                    , 16
                    , 3000
                    )
            shutil.rmtree(upload_path)
            os.mkdir(upload_path)
            chown_dir()
            
    
    upload_info_text=ft.Text(f"", size=16, weight=ft.FontWeight.BOLD)
    
    dlg = ft.AlertDialog(
        title=ft.Text(f"UPLOAD COMPLETE", size=17, weight=ft.FontWeight.BOLD)
    )
    
    def open_dlg():
        page.dialog = dlg
        dlg.open = True
        page.update()
        
    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def close_dlg(e):
        dlg_modal.open = False
        page.update()
        
    def delete_upload_dir(e):
        shutil.rmtree(upload_path)
        os.mkdir(upload_path)
        chown_dir()
        snackBar(
                f"Local Directory Has Been Emptied"
                , 'GREY'
                , 16
                , 3000
                )
        
    def init_page():
        select_file_btn.disabled = True
        empty_uploadDir_btn.disabled = True
        page.controls.remove(upload_file_btn)
        page.controls.insert(1, passwd_validate_btn)
        files.current.controls.clear()
        page.update()

    def check_passwd(e, passwd):
        if passwd == os.environ.get('PERSONAL_PASSWORD'):
            dlg_modal.open = False
            select_file_btn.disabled = False
            empty_uploadDir_btn.disabled = False
            snackBar("WELCOME!", 'GREEN', 16, 3000)
            passwd_field.value = ""
            page.controls.insert(1, upload_file_btn)
            page.controls.remove(passwd_validate_btn)
            page.update()
        else:
            snackBar("ENTER VALID PASSWORD", 'RED', 16, 3000)
            dlg_modal.open = True
            passwd_field.value = ""
            page.update()

    passwd_validate_btn = ft.FloatingActionButton(
                content=ft.Row([ft.Icon(ft.icons.LOCK), ft.Text("Validate")], alignment="center", spacing=8),
                ref=upload_button,
                bgcolor=ft.colors.RED_400,
                shape=ft.RoundedRectangleBorder(radius=20),
                width=120,
                mini=True,
                on_click=open_dlg_modal,
            )

    select_file_btn = ft.ElevatedButton(
                "Select files...",
                icon=ft.icons.FOLDER_OPEN,
                on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                disabled=True,
            )
    
    upload_file_btn = ft.FloatingActionButton(
                content=ft.Row([ft.Icon(ft.icons.UPLOAD), ft.Text("Upload")], alignment="center", spacing=8),
                ref=upload_button,
                bgcolor=ft.colors.GREEN_400,
                shape=ft.RoundedRectangleBorder(radius=20),
                width=120,
                mini=True,
                on_click=upload_files,
            )

    empty_uploadDir_btn = ft.ElevatedButton(
                content=ft.Icon(ft.icons.DELETE),
                bgcolor=ft.colors.GREY_300,
                disabled=True,
                on_click=delete_upload_dir
            )

    upload_btn_row = ft.Row(controls=[select_file_btn, empty_uploadDir_btn],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    passwd_field = ft.TextField(
        label="password",
        keyboard_type='NUMBER',
        border="underline",
        width=100,
        height=50,
        text_size=20,
        color='BLUE',
        password=True,
        can_reveal_password=True
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("ENTER PASSWORD", size=16, weight=ft.FontWeight.BOLD),
        content=passwd_field,
        actions=[
            ft.TextButton("취소", on_click=close_dlg),
            ft.TextButton("확인", on_click=lambda e: check_passwd(e, passwd_field.value)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )        

    page.overlay.append(file_picker)

    page.add(
        passwd_validate_btn,
        upload_btn_row,
        ft.Column(ref=files),
    )
    
ft.app(target=main
    , upload_dir=os.environ.get('UPLOAD_DIR_NAME')
    , port = 2000
    , view=ft.WEB_BROWSER)