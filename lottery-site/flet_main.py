import flet as ft
import random
from pytz import timezone
from datetime import datetime
from lottery_database import lottoDB

cursor = lottoDB.cursor()
tableName = "lotto"
lottery_number = [str(i).zfill(2) for i  in range(1,46)]
currentTime = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')

def main(page: ft.Page):
    page.title = "Special Lottery Number"
    page.bgcolor = ft.colors.WHITE30
    page.scroll = "always"
    page.padding = 20
    day_list = []
    
    def insertDataToDB():
        try:
            sql = f"INSERT INTO {tableName} (conntime, ipaddr, number, gamecnt) VALUES(%s, %s, %s, %s)"
            val = (currentTime, page.client_ip, ",".join(day_list), cnt_text.value)
            cursor.execute(sql,val)
            lottoDB.commit()
        except Exception as e:
            print(e)
        

    def snackBar(msg, color):
        page.snack_bar = ft.SnackBar(
                ft.Text(msg, size=17, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                duration=2000,
                )
        page.snack_bar.open = True
        page.update()


    def checkbox_changed(e):
        if check_box1.value:
            snackBar("입력하신 기념일 숫자 조합만 사용됩니다.\n해제시 다른 숫자도 함께 조합될 수 있습니다.", 'blue')
        if check_box2.value:
            snackBar("1의 자리와 10의 자리가 바뀐 숫자도 사용됩니다.\n(숫자가 91이면 19로 사용)", 'blue')
        else: pass

    def deleteDayList(day_list):
        day_list.clear()

    def deleteall(e):
        memo.value = ""
        cnt_text.value = ""
        lotto_memo.value = ""
        check_box1.value = False
        check_box2.value = False
        deleteDayList(day_list)
        day_list.clear()
        snackBar("모든 데이터가 삭제되었습니다.", 'red')
        page.update()

    def addToText(e):
        if len(number_text.value) == 6 and number_text.value.isdigit():
            try:
                day_list.append(number_text.value)
                numbs = [i for i in day_list]
                vals = '\n'.join(numbs)
                memo.value = vals
                snackBar(f"{number_text.value} 추가되었습니다.", 'green')
            except ValueError:
                snackBar("문제가 발생하였습니다.", 'red')
        else:
            snackBar("여섯자리 숫자만 입력해주세요.", 'red')

        number_text.value = ""
        page.update()
        
    def lotto_create(e):
        numb_list = []
        final_number = []
        numbs = [i for i in day_list]
        for n in numbs:
            numb_list += [n[i*2:i*2+2] for i in range(len(n)//2)]
            if check_box2.value:
                numb_list += [n[::-1][i*2:i*2+2] for i in range(len(n)//2)]
        numb_set = list(set(numb_list))
        for i in range(len(numb_set)):
            number = int(numb_set[i])
            if number > 45:
                numb_set[i] = str(divmod(number,45)[-1]).zfill(2)
        numb_set = [i for i in list(set(numb_set)) if int(i) > 0]
        extra_set = [i for i in lottery_number if i not in numb_set]
        if len(numb_set) < 8:
            snackBar("데이터가 부족합니다. 기념일을 더 넣어주세요", 'red')
        else:
            cnt = 0
            added_set = [] if check_box1.value else random.sample(extra_set, len(numb_set)//2)
            try: 
                lotto_cnt = int(cnt_text.value)
                if lotto_cnt <= 0:
                    snackBar("1 이상의 숫자만 입력해주세요", 'red')
                else:
                    while cnt < lotto_cnt:
                        num = random.sample(numb_set+added_set, 6)
                        sorted_num = sorted(num, key=lambda x: int(x))
                        if sorted_num not in final_number:
                            fin = '  '.join(sorted_num)
                            final_number.append(fin)
                            cnt += 1
                        else:
                            pass
                        
                    final_vals = '\n'.join(final_number)
                    lotto_memo.value = final_vals
                    insertDataToDB()
                    page.update()
            except ValueError:
                snackBar("숫자만 입력해주세요", 'red')
        
    number_text = ft.TextField(label="기념일(yymmdd)", keyboard_type='NUMBER', color='BLACK', width=250)
    btn1 = ft.TextButton(content=ft.Text("입력", color="BLUE", weight=ft.FontWeight.BOLD, size=17), on_click=addToText)
    day_row = ft.Row(controls=[number_text, btn1])
    
    cnt_text = ft.TextField(label="게임 개수", keyboard_type='NUMBER', color='BLACK', width=100)
    check_text1 = ft.Text("기념일 숫자만 사용", color='BLACK')
    check_box1 = ft.Checkbox(value=False, on_change=checkbox_changed)
    
    check_text2 = ft.Text("숫자 반전 사용", color='BLACK')
    check_box2 = ft.Checkbox(value=False, on_change=checkbox_changed)
    
    check1 = ft.Row(controls=[check_text1, check_box1])
    check2 = ft.Row(controls=[check_text2, check_box2])
    delete_bnt = ft.FloatingActionButton(text="초기화", on_click=deleteall, width=100, bgcolor=ft.colors.RED_200)
    load_bnt = ft.ElevatedButton(text="로또 번호 생성", on_click=lotto_create)
    btn_container1 = ft.Container(content=load_bnt, padding=5)
    memo = ft.TextField(label="입력한 기념일", multiline=True, color='BLACK', width=300)
    lotto_memo = ft.TextField(label="추천 번호", multiline=True, color='BLACK', width=300)
    page.add(
        day_row
        , check1
        , check2
        , memo
        , ft.Row(controls=[cnt_text, btn_container1])
        , delete_bnt
        , lotto_memo
    )


ft.app(target=main
       , name = ''
       , view = ft.WEB_BROWSER
       , port = 2010
       )