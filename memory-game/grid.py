import random
import flet as ft

colors = {"empty":"#5c443b", "target":"#4cbbb5"}

class GenerateGrid(ft.UserControl):
    
    def __init__(self, difficulty):
        self.grid = ft.Column(opacity=0, animate_opacity=300)
        self.correct: int = 0
        self.incorrect: int = 0
        self.blue_tiles: int = 0
        self.difficulty: int = difficulty
        super().__init__()
        
    def show_color(self, e):
        # target 색이면 target 색 그대로 보여줌
        if e.control.data == colors["target"]:
            if e.control.bgcolor == colors["empty"]:
                e.control.bgcolor = colors["target"]
                e.control.opacity = 1
                e.control.update()
                self.correct += 1
                e.page.update()
            else: pass
        # target 색 아니면 빨간색 보여줌
        else:
            if e.control.bgcolor == colors["empty"]:
                e.control.bgcolor = "#982c33"
                e.control.opacity = 1
                e.control.update()
                self.incorrect += 1
                e.page.update()
            else: pass
        
    def build(self):
        rows = [
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER
                , controls=[
                    ft.Container(
                        width=54
                        , height=54
                        , animate= 300
                        , border=ft.border.all(1, "white")
                        , on_click=lambda e: self.show_color(e)    
                    )
                    for _ in range(5)
                ]
            )
            for _ in range(5)
        ]
        
        
        while True:
            color_list = []
            for row in rows:
                for container in row.controls:
                    # random.choices의 weight : colors 의 인자들이 뽑힐 수 있는 가중치. 
                    # target list 개수와 weights 인자의 개수가 동일해야한다.
                    container.bgcolor = random.choices(list(colors.values()), weights=[10, self.difficulty])[0]
                    color_list.append(random.choices(list(colors.values()), weights=[10, self.difficulty])[0])
                    container.data = container.bgcolor
                    
                    if container.bgcolor == colors["target"]:
                        self.blue_tiles += 1
            if color_list.count(colors["target"]) >= 3:
                break
        
        self.grid.controls = rows
        
        return self.grid
