"""
bullet.py — 玩家飞船发射的单个子弹。

普通子弹垂直向上飞行（vx = 0）。
散弹子弹创建时 vx = ±2，
使三发子弹在向上飞行的同时，向左右轻微散开。

子弹使用 pygame.draw.rect 直接绘制矩形，无需加载图片，性能更轻量。
"""

import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """屏幕上的一颗子弹，向上飞行（可附带横向偏移）。

    属性
    ----------
    vx          水平漂移速度（像素/帧）。普通子弹为0；
                负值向左飘，正值向右飘（散弹模式）。
    speed_factor 垂直飞行速度。创建时从设置中读取，
                 但连射模式会在 game_events.fire_bullet() 中提升速度。
    """

    def __init__(self, ai_settings, screen, ship, vx=0):
        """在飞船顶端位置创建一颗子弹。

        参数
        ----------
        ai_settings  全局游戏配置（速度、尺寸、颜色）。
        screen       绘制用的 pygame 窗口。
        ship         用于将子弹定位在飞船当前中心上方。
        vx           可选水平漂移速度，默认为0。
        """
        super().__init__()
        self.screen = screen
        self.vx     = vx    # 水平漂移 —— 普通子弹为0

        # 先创建矩形，再根据飞船位置调整，让子弹看起来从飞船头部射出
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = ship.rect.centerx  # 与飞船水平居中对齐
        self.rect.top     = ship.rect.top       # 与飞船顶部齐平

        # 浮点数位置，实现平滑移动（与飞船、外星人逻辑一致）
        self.y = float(self.rect.y)

        self.color        = ai_settings.bullet_color
        self.speed_factor = ai_settings.bullet_speed_factor  # 连射模式可覆盖该速度

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        """向上移动子弹（如果 vx 不为0则同时横向漂移）。

        浮点数 self.y 累积小数位运动；
        self.rect.y 是用于碰撞与绘制的整数版本。
        """
        self.y      -= self.speed_factor    # 向上移动（y越小越靠上）
        self.rect.y  = int(self.y)

        if self.vx:
            self.rect.x += self.vx         # 散弹模式的斜向漂移

    # ─────────────────────────────────────────────────────────────────
    def draw_bullet(self):
        """在屏幕上绘制实心矩形子弹。"""
        pygame.draw.rect(self.screen, self.color, self.rect)