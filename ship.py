"""
ship.py — 玩家控制的飞船，带惯性物理的四向移动系统。

移动物理模型
──────────────
飞船不会瞬间达到目标速度，而是先**加速**到最大速度，
松开方向键后通过**摩擦系数减速**，最终慢慢停下。
这种设计带来流畅的“太空漂浮感”，同时又不会难以控制：

    速度 += 加速度    （按住方向键时）
    速度 *= 摩擦系数  （未按键时 —— 让速度逐渐趋近于0）

每一帧都会把速度限制在 ±最大速度 范围内，
极小的残留速度会直接设为0，避免无限微移。
"""

import pygame
from pygame.sprite import Sprite


class Ship(Sprite):
    """玩家飞船：带惯性的四向移动控制。

    飞船图像也会被用作计分板上的生命图标（prep_ships），
    因此即使在屏幕外创建用于显示图标的飞船实例，构造函数也必须正常工作。
    """

    def __init__(self, ai_settings, screen):
        """加载飞船图像，并设置初始位置（屏幕底部中央）。"""
        super().__init__()
        self.screen     = screen
        self.ai_settings = ai_settings

        # 加载飞船图像并获取其外接矩形
        self.image      = pygame.image.load("images/ship.bmp")
        self.rect       = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # 将飞船放在屏幕底部中央
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom  = self.screen_rect.bottom

        # 使用浮点数存储位置，实现低速移动时的亚像素精度
        # 每一帧再将浮点数位置更新到整数矩形中
        self.centerx = float(self.rect.centerx)
        self.centery = float(self.rect.centery)

        # ── 物理参数 ────────────────────────────────────────
        # 所有参数都基于飞船基础速度，确保统一手感
        base_speed = ai_settings.ship_speed_factor

        # 水平方向 —— 全速横向闪避，手感更跟手
        self.accel_x     = base_speed * 0.22   # 每帧水平加速度
        self.max_speed_x = base_speed * 2.6    # 水平最大速度

        # 垂直方向 —— 刻意设计得更慢，防止飞船直接冲入外星人舰队
        # 垂直加速度约为水平的45%；最大速度约为水平的46%
        self.accel_y     = base_speed * 0.10   # 更柔和的垂直推力
        self.max_speed_y = base_speed * 1.2    # 更低的垂直速度上限

        # 全方向共用参数
        self.friction            = 0.82   # 松开按键时减速更快，控制更精准，减少漂移
        self.min_velocity_cutoff = 0.05   # 小于该值 → 直接设为0

        # 当前速度（初始静止）
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # ── 移动标志 ────────────────────────────────────────────
        # 按键按下时设为True，松开时设为False（见 game_events.py）
        self.moving_right = False
        self.moving_left  = False
        self.moving_up    = False
        self.moving_down  = False

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        """应用加速度/摩擦力，限制速度，检测屏幕边界。

        游戏运行且未暂停时，主循环每帧调用一次。
        """

        # ── 水平方向 ───────────────────────────────────────────
        if self.moving_right and not self.moving_left:
            self.velocity_x += self.accel_x
        elif self.moving_left and not self.moving_right:
            self.velocity_x -= self.accel_x
        else:
            # 无水平输入 → 摩擦减速
            self.velocity_x *= self.friction

        # ── 垂直方向（速度更慢，避免直冲敌群）────────────
        if self.moving_down and not self.moving_up:
            self.velocity_y += self.accel_y
        elif self.moving_up and not self.moving_down:
            self.velocity_y -= self.accel_y
        else:
            self.velocity_y *= self.friction

        # ── 分别限制各方向最大速度 ─────────────────────
        self.velocity_x = max(-self.max_speed_x, min(self.velocity_x, self.max_speed_x))
        self.velocity_y = max(-self.max_speed_y, min(self.velocity_y, self.max_speed_y))

        # 极小速度直接归零，避免无限微移
        if abs(self.velocity_x) < self.min_velocity_cutoff:
            self.velocity_x = 0.0
        if abs(self.velocity_y) < self.min_velocity_cutoff:
            self.velocity_y = 0.0

        # ── 根据速度更新位置 ────────────────────────────────────────
        self.centerx += self.velocity_x
        self.centery += self.velocity_y

        # ── 屏幕边界限制 ──────────────────────────────────
        # 计算允许的最小/最大中心位置，使飞船不会部分移出屏幕
        half_w = self.rect.width  / 2
        half_h = self.rect.height / 2

        if self.centerx < half_w:
            self.centerx = half_w;  self.velocity_x = 0.0
        elif self.centerx > self.screen_rect.width - half_w:
            self.centerx = self.screen_rect.width - half_w;  self.velocity_x = 0.0

        if self.centery < half_h:
            self.centery = half_h;  self.velocity_y = 0.0
        elif self.centery > self.screen_rect.height - half_h:
            self.centery = self.screen_rect.height - half_h;  self.velocity_y = 0.0

        # 将浮点数位置更新到整数矩形
        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)

    # ─────────────────────────────────────────────────────────────────
    def blitme(self):
        """在当前位置绘制飞船。"""
        self.screen.blit(self.image, self.rect)

    # ─────────────────────────────────────────────────────────────────
    def center_ship(self):
        """将飞船重置到底部中央，并清空速度。

        失去生命后调用，确保玩家复活时
        位置固定、无任何惯性残留。
        """
        self.centerx = float(self.screen_rect.centerx)
        self.rect.bottom = self.screen_rect.bottom
        self.centery = float(self.rect.centery)

        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.rect.centerx = int(self.centerx)
        self.rect.centery = int(self.centery)