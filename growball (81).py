from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.text import LabelBase
import random

LabelBase.register(name="MapleFont", fn_regular="/storage/emulated/0/Download/Maplestory Light.ttf")

class Ball:
    def __init__(self, x, y, dx, dy, floor_reward, wall_reward, atk, size=30):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.floor_reward = floor_reward
        self.wall_reward = wall_reward
        self.atk = atk
        self.super_jump = False
        self.size = size

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.falling = False

class Boss:
    def __init__(self, x, y, max_hp):
        self.x = x
        self.y = y
        self.hp = max_hp
        self.max_hp = max_hp
        self.size = 80

class GameArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gravity = -0.3
        self.base_dy = 8
        self.default_floor_reward = 1
        self.default_wall_reward = 2
        self.default_dx = 4
        self.default_atk = 1
        self.gold = 0

        self.cost_add = 10
        self.cost_speed = 30
        self.cost_floor = 10
        self.cost_wall = 8
        self.cost_star_rate = 100
        self.cost_jump_rate = 200
        self.cost_atk = 25

        self.star_spawn_interval = 30
        self.super_jump_chance = 0.001
        self.star_timer = 0
        self.star = None

        self.balls = []
        self.boss_toggle = False
        self.boss = None
        self.boss_max_hp = 100

        Clock.schedule_interval(self.update, 1/60)
        self.bind(size=self.reset_positions)

    def create_ball(self):
        return Ball(
            x=self.width // 2,
            y=self.height * 0.35,  # 버튼 높이만큼 위에서 시작
            dx=random.choice([-1, 1]) * self.default_dx,
            dy=self.base_dy,
            floor_reward=self.default_floor_reward,
            wall_reward=self.default_wall_reward,
            atk=self.default_atk
        )

    def reset_positions(self, *args):
        self.balls = [self.create_ball()]

    def spawn_star(self):
        if not self.star:
            self.star = Star(self.width//2, self.height * 0.9)

    def spawn_boss(self):
        if not self.boss:
            self.boss = Boss(self.width//2 - 40, self.y + 2, self.boss_max_hp)

    def update(self, dt):
        self.star_timer += dt
        if self.star_timer >= self.star_spawn_interval:
            self.star_timer = 0
            self.spawn_star()

        if self.star and self.star.falling:
            self.star.y += self.gravity * 3
            if self.star.y <= self.y:
                self.gold += self.default_floor_reward * 100
                self.star = None

        if self.boss_toggle:
            self.spawn_boss()

        for ball in self.balls:
            ball.dy += self.gravity
            ball.x += ball.dx
            ball.y += ball.dy

            if ball.y <= self.y:
                ball.y = self.y
                if random.random() < self.super_jump_chance:
                    ball.dy = self.base_dy * 4
                    ball.super_jump = True
                else:
                    ball.dy = self.base_dy * random.uniform(0.8, 1.2)
                    ball.super_jump = False
                self.gold += ball.floor_reward

            if ball.x <= 0:
                ball.x = 0
                ball.dx *= -random.uniform(0.8, 1.2)
                self.gold += ball.wall_reward
            elif ball.x + ball.size >= self.width:
                ball.x = self.width - ball.size
                ball.dx *= -random.uniform(0.8, 1.2)
                self.gold += ball.wall_reward

            if self.star and not self.star.falling and ball.super_jump and abs(ball.y + ball.size - self.star.y) < 25:
                self.star.falling = True

            if self.boss and abs(ball.x - self.boss.x) < self.boss.size and abs(ball.y - self.boss.y) < self.boss.size:
                self.boss.hp -= ball.atk
                if self.boss.hp <= 0:
                    self.gold += (self.default_floor_reward + self.default_wall_reward) * 8
                    self.boss_max_hp += 50
                    self.boss = None

        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.3, 0.3, 0.3)
            Rectangle(pos=(0, self.y), size=(self.width, 2))
            Color(1, 0.5, 0.2)
            for ball in self.balls:
                Ellipse(pos=(ball.x, ball.y), size=(ball.size, ball.size))
            if self.star:
                Color(1, 1, 0)
                Ellipse(pos=(self.star.x, self.star.y), size=(25, 25))
            if self.boss:
                Color(1, 0, 0)
                Rectangle(pos=(self.boss.x, self.boss.y), size=(self.boss.size, self.boss.size))

class TycoonApp(App):
    def build(self):
        self.game_area = GameArea()
        self.game_area.size_hint = (1, 0.6)
        layout = BoxLayout(orientation='vertical')

        self.gold_label = Label(font_name="MapleFont", font_size=20, size_hint=(1, 0.05))

        layout.add_widget(self.gold_label)
        layout.add_widget(self.game_area, 1)

        panel = BoxLayout(orientation='vertical', size_hint=(1, 0.35))
        row1 = BoxLayout()
        row2 = BoxLayout()
        row3 = BoxLayout()

        def make_button(text, callback):
            btn = Button(text=text, font_name="MapleFont", font_size=14)
            btn.bind(on_press=callback)
            return btn

        self.btn_add = make_button("", self.add_ball)
        self.btn_speed = make_button("", self.up_speed)
        self.btn_floor = make_button("", self.up_floor)
        self.btn_wall = make_button("", self.up_wall)
        self.btn_star = make_button("", self.up_star)
        self.btn_jump = make_button("", self.up_jump)
        self.btn_atk = make_button("", self.up_atk)
        self.btn_boss = make_button("보스 생성", self.toggle_boss)

        row1.add_widget(self.btn_add)
        row1.add_widget(self.btn_speed)
        row1.add_widget(self.btn_floor)
        row2.add_widget(self.btn_wall)
        row2.add_widget(self.btn_star)
        row2.add_widget(self.btn_jump)
        row3.add_widget(self.btn_atk)
        row3.add_widget(self.btn_boss)

        panel.add_widget(row1)
        panel.add_widget(row2)
        panel.add_widget(row3)

        layout.add_widget(panel)

        Clock.schedule_interval(lambda dt: self.update_ui(), 1/30)
        return layout

    def update_ui(self):
        g = self.game_area
        self.gold_label.text = f"골드: {int(g.gold)}"
        self.btn_add.text = f"공 추가\n{len(g.balls)}개\n{round(g.cost_add)}G"
        self.btn_speed.text = f"속도 +\n{round(g.default_dx)}\n{round(g.cost_speed)}G"
        self.btn_floor.text = f"땅 보상\n{g.default_floor_reward}\n{round(g.cost_floor)}G"
        self.btn_wall.text = f"벽 보상\n{g.default_wall_reward}\n{round(g.cost_wall)}G"
        self.btn_star.text = f"별 주기\n{g.star_spawn_interval}s\n{round(g.cost_star_rate)}G"
        self.btn_jump.text = f"슈퍼점프\n{round(g.super_jump_chance*100, 2)}%\n{round(g.cost_jump_rate)}G"
        self.btn_atk.text = f"공격력\n{g.default_atk}\n{round(g.cost_atk)}G"
        self.btn_boss.text = "보스 삭제" if g.boss_toggle else "보스 생성"

    def add_ball(self, instance):
        g = self.game_area
        if g.gold >= g.cost_add:
            g.gold -= round(g.cost_add)
            g.balls.append(g.create_ball())
            g.cost_add *= 1.5

    def up_speed(self, instance):
        g = self.game_area
        if g.gold >= g.cost_speed:
            g.gold -= round(g.cost_speed)
            g.default_dx += 1
            g.cost_speed *= 1.3

    def up_floor(self, instance):
        g = self.game_area
        if g.gold >= g.cost_floor:
            g.gold -= round(g.cost_floor)
            g.default_floor_reward += 1
            g.cost_floor *= 1.2

    def up_wall(self, instance):
        g = self.game_area
        if g.gold >= g.cost_wall:
            g.gold -= round(g.cost_wall)
            g.default_wall_reward += 1
            g.cost_wall *= 1.2

    def up_star(self, instance):
        g = self.game_area
        if g.gold >= g.cost_star_rate and g.star_spawn_interval > 1:
            g.gold -= round(g.cost_star_rate)
            g.star_spawn_interval -= 1
            g.cost_star_rate *= 2.1

    def up_jump(self, instance):
        g = self.game_area
        if g.gold >= g.cost_jump_rate:
            g.gold -= round(g.cost_jump_rate)
            g.super_jump_chance += 0.0001
            g.cost_jump_rate *= 1.9

    def up_atk(self, instance):
        g = self.game_area
        if g.gold >= g.cost_atk:
            g.gold -= round(g.cost_atk)
            g.default_atk += 1
            g.cost_atk *= 1.6

    def toggle_boss(self, instance):
        g = self.game_area
        g.boss_toggle = not g.boss_toggle
        if not g.boss_toggle:
            g.boss = None

TycoonApp().run()