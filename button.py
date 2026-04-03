"""
button.py — 使用 pygame 直接渲染的可点击文本按钮。

游戏中只存在一个按钮实例（开始按钮）。
它会显示在标题界面/游戏结束界面，游戏开始后隐藏。
点击检测在 game_events.check_play_button() 中通过
play_button.rect.collidepoint(mouse_x, mouse_y) 实现。
"""

import pygame.font


class Button:
    """带居中文字标签的矩形按钮。

    按钮表面在 prep_msg() 中只渲染一次，之后每帧直接绘制 ——
    游戏过程中不会每帧都调用 font.render()。
    """

    def __init__(self, ai_settings, screen, msg):
        """创建按钮矩形并预渲染文字标签。

        参数
        ----------
        ai_settings  此处未直接使用，但保留以保持接口统一
        screen       主显示窗口（用于居中定位）
        msg          按钮上显示的文字（如 "Play"）
        """
        self.screen      = screen
        self.screen_rect = screen.get_rect()

        # ── 按钮外观 ─────────────────────────────────────────
        self.width, self.height = 200, 50
        self.button_color = (0, 255, 0)     # 亮绿色背景
        self.text_color   = (255, 255, 255) # 白色文字
        self.font         = pygame.font.SysFont(None, 48)

        # ── 几何位置 ──────────────────────────────────────────────────
        # 将按钮放在屏幕正中央
        self.rect        = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # 预渲染标签（只执行一次）
        self.prep_msg(msg)

    # ─────────────────────────────────────────────────────────────────
    def prep_msg(self, msg):
        """将文字渲染为表面并居中放置在按钮内。

        如果运行时需要修改按钮文字，可再次调用此方法。
        """
        self.msg_image      = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    # ─────────────────────────────────────────────────────────────────
    def draw_button(self):
        """先填充按钮颜色，再绘制文字。"""
        # 使用 rect 参数的 screen.fill 比绘制 Surface 更快
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)