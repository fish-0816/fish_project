"""
alien.py — 单个外星人精灵，以编队形式左右移动。

外星人自身不决定何时改变方向 —— 该逻辑在 game_updates.py 中
（check_fleet_edges / change_fleet_direction）。
每个外星人只需从设置中读取 fleet_direction 并相应移动。
当舰队反转方向时，下一次调用 update() 所有外星人会自动向反方向移动。
"""

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """入侵舰队中的单个外星人。

    位置使用浮点数（self.x）存储，即使低速下也能实现平滑的亚像素移动；
    self.rect.x 是用于绘制和碰撞检测的整数副本。
    """

    def __init__(self, ai_settings, screen):
        """加载外星人图像，并将其初始放在左上角附近。

        确切的初始位置会被 game_updates.py 中的 create_alien() 覆盖 ——
        这里仅提供安全默认值，确保在正式放置前矩形运算能正常工作。
        """
        super().__init__()
        self.screen      = screen
        self.ai_settings = ai_settings

        # 加载共享的外星人图像（所有外星人使用同一张图片）
        self.image = pygame.image.load("images/alien.bmp")
        self.rect  = self.image.get_rect()

        # 默认位置：距离左上角一个外星人宽度的位置
        # create_fleet() 会为每个真实外星人覆盖该位置
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 水平位置的浮点数副本 —— 每帧更新，确保小数速度正确累积
        self.x = float(self.rect.x)

    # ─────────────────────────────────────────────────────────────────
    def check_edges(self):
        """如果外星人到达屏幕左/右边缘，返回 True。

        由 game_updates.py 中的 check_fleet_edges() 每帧调用。
        只要舰队中有任何一个外星人返回 True，整个舰队就会
        反转方向并向下移动 fleet_drop_speed 像素。
        """
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        """根据当前舰队方向移动外星人一步。

        fleet_direction 为 +1（向右）或 -1（向左），
        通过 ai_settings 对象在所有外星人间共享。
        """
        self.x += self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction
        self.rect.x = int(self.x)  # 将浮点数转为整数用于绘制

    # ─────────────────────────────────────────────────────────────────
    def blitme(self):
        """在当前位置绘制外星人（用于调试）。"""
        self.screen.blit(self.image, self.rect)

