import flet as ft
import time
from grid import GenerateGrid
from countdown import Countdown

is_running = True
def main(page: ft.Page):
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    trial_count = 3
    time_count = 30
    level_count = 5
    cnt_ = 0
    trial = ft.Text(size=13, weight='bold')
    result = ft.Text(size=16, weight='bold', text_align=ft.TextAlign.CENTER)
    stage = ft.Text(size=13, weight='bold')
    selectStage = ft.TextField(label="Stage"
                               , hint_text="Stage 입력 (1-6)"
                               , width=200
                               , keyboard_type='NUMBER')
    
    start_button = ft.Container(
        content=ft.ElevatedButton(
            on_click=lambda e: start_game(2
                                          , GenerateGrid(2)
                                          , Countdown(time_count)
                                          , cnt_
                                          , level_count
                                          , is_running)
            , content=ft.Text("START!", size=13, weight='bold')
            , style=ft.ButtonStyle(
                shape={"":ft.RoundedRectangleBorder(radius=8)}, color={"":"white"}
            )   
            , height=45
            , width=255
        )
    )
    
    
    def snackBar(msg, color):
        page.snack_bar = ft.SnackBar(
                ft.Text(msg, size=17, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                duration=2000,
                )
        page.snack_bar.open = True
        page.update()    

    def change_state(e):
        # print(globals()["is_running"])
        globals()["is_running"] = False
        # print(globals()["is_running"])

        
    # int(selectStage.value)
    def start_game(e, level, timer, cnt_, level_count, is_running):
        globals()["is_running"] = True
        if selectStage.value.isdigit():
            result.value = ""
            trial.value = f"Trial Left : {trial_count}"
            trial.update()
            if cnt_ == 0:
                page.controls.remove(selectStage)
                level_count = int(selectStage.value)
                page.update()
            
            grid = level
            countdown = timer
                
            page.controls.insert(2, countdown)
            page.controls.insert(3, grid)
            page.update()
            
            grid.grid.opacity = 1
            grid.grid.update()
            stage.value = f"Stage : {grid.difficulty-1}/{level_count}"
            stage.update()

            # start_button.disabled = True
            # container 내부 elevatedbutton level 조작
            start_button.content.disabled = True
            start_button.content.content.value = 'EXIT'
            
            # container level 조작
            start_button.bgcolor = ft.colors.RED_300
            start_button.border_radius = 8
            start_button.on_click = change_state
            start_button.update()
            
            time.sleep(1.5 - 0.2*(grid.difficulty-2))
            
            for rows in grid.grid.controls:
                for container in rows.controls:
                    if container.bgcolor == "#4cbbb5":
                        container.bgcolor = "#5c443b"
                        container.update()
            while globals()["is_running"]:
                
                trial.value = f"Trial Left : {trial_count - grid.incorrect}"
                trial.update()
                
                if countdown.seconds == 0:
                    trial.value = f""
                    trial.update()
                    result.value = "SORRY. You ran out if time"
                    result.color = "red700"
                    result.update()
                    time.sleep(2)
                    cnt_ = 0
                    break
                    
                
                if grid.correct == grid.blue_tiles:
                    grid.grid.disable = True
                    grid.grid.update()
                    
                    result.value = "GOOD JOB!"
                    result.color = "green700"
                    result.update()
                    
                    time.sleep(3)
                    result.value = ""
                    page.controls.remove(countdown)
                    page.controls.remove(grid)
                    page.update()
                    
                    difficulty = grid.difficulty + 1
                    
                    if grid.difficulty == level_count + 1:
                        break
                    else:
                        cnt_ += 1
                        start_game(e
                                , GenerateGrid(difficulty)
                                , Countdown(time_count - 5*(difficulty-2))
                                , cnt_
                                , level_count
                                , is_running)
                    break
                
                if grid.incorrect == trial_count:
                    trial.value = f"Trial Left : 0"
                    result.value = "SORRY. You ran out chances"
                    result.color = "red700"
                    trial.update()
                    result.update()
                    time.sleep(2)
                    result.value = ""
                    stage.value = ""
                    page.controls.remove(countdown)
                    page.controls.remove(grid)
                    start_button.disabled = False
                    start_button.content.disabled = False
                    start_button.content.content.value = 'Start!'
                    start_button.bgcolor = ft.colors.BLACK54
                    start_button.border_radius = 8
                    start_button.content.on_click = lambda e: start_game(2
                                            , GenerateGrid(2)
                                            , Countdown(time_count)
                                            , cnt_
                                            , level_count
                                            , is_running)
                    start_button.update()
                    page.update()
                    cnt_ = 0
                    break
                
            if globals()["is_running"] and countdown.seconds != 0:             
                if grid.difficulty == level_count + 1 and grid.incorrect != trial_count:
                    trial.value = ""
                    result.value = "CONGRATULATIONS! \nYou have completed all steps!"
                    result.color = "green700"
                    start_button.disabled = True
                    result.size = 20
                    stage.value = ""
                    trial.update()
                    start_button.update()
                    result.update()
                    stage.update()
                    time.sleep(3)
                    start_button.disabled = False
                    start_button.content.disabled = False
                    start_button.content.content.value = 'Start!'
                    start_button.bgcolor = ft.colors.BLACK54
                    start_button.border_radius = 8
                    start_button.content.on_click = lambda e: start_game(2
                                            , GenerateGrid(2)
                                            , Countdown(time_count)
                                            , cnt_
                                            , level_count
                                            , is_running)
                    result.value = ""
                    result.update()
                    page.update()
                    start_button.update()
                    cnt_ = 0
                else:
                    trial.value = ""
                    trial.update()
                    cnt_ = 0
                        
                page.controls.insert(3, selectStage)
                page.update()
                selectStage.value = ""
                selectStage.update()
            else:
                page.controls.remove(countdown)
                page.controls.remove(grid)
                page.controls.insert(3, selectStage)
                page.update()
                result.value = ""
                result.update()
                selectStage.value = ""
                selectStage.update()
                start_button.disabled = False
                start_button.content.disabled = False
                start_button.content.content.value = 'Start!'
                stage.value = ""
                trial.value = ""
                # container level 조작
                start_button.bgcolor = ft.colors.BLACK54
                start_button.border_radius = 8
                start_button.content.on_click = lambda e: start_game(2
                                          , GenerateGrid(2)
                                          , Countdown(time_count)
                                          , cnt_
                                          , level_count
                                          , is_running)
                stage.update()
                trial.update()
                start_button.update()
                cnt_ = 0
                
        else:
            snackBar("Please Input the Stage", 'red')
        

############################ PAGE ADD #################################
    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER
            , controls=[
                ft.Text("Memory Matrix"
                        , size=22
                        , weight="bold")
            ]
        ),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[result]),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[trial]),
        ft.Divider(height=10, color='transparent'),
        selectStage,
        ft.Divider(height=10, color='transparent'),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[stage]),
        ft.Divider(height=10, color='transparent'),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[start_button]),
    )
    
    page.update()
    
ft.app(target=main
       , name = ''
       , view = ft.WEB_BROWSER
       , port = 2020
       )