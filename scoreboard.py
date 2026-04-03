"""
scoreboard.py — 渲染所有 HUD 文本和剩余生命图标行。

计分板会将文本表面预渲染并缓存为图像属性（如 self.score_image），
因此只有数值真正变化时才调用 font.render()，而非每帧都渲染。
show_score() 只需直接绘制缓存图像 —— 性能非常高效。

界面布局（屏幕顶部）
──────────────────────
  [飞船图标]   [当前分数]   [最高分（居中）]   [关卡]
                                               [关卡（分数下方）]
"""

import pygame.font
from pygame.sprite import Group
from ship import Ship


class Scoreboard:
    """HUD 界面：分数、最高分、关卡数和生命图标。

    所有文本表面都会预渲染，仅在数值变化时通过 prep_*() 方法更新。
    主循环每帧只需调用 show_score()。
    """

    def __init__(self, ai_settings, screen, stats):
        """预渲染所有初始 HUD 表面。

        参数
        ----------
        ai_settings  用于获取背景色，使文字与背景无缝融合
        screen       主显示窗口
        stats        游戏状态实时引用，每次调用 prep_*() 时读取
        """
        self.screen      = screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats       = stats

        # ── 字体设置 ────────────────────────────────────────────────
        self.text_color = (30, 30, 30)              # 灰色背景上的近黑色文字
        self.font       = pygame.font.SysFont(None, 48)

        # 初始化所有 HUD 元素
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    # ─────────────────────────────────────────────────────────────────
    def prep_score(self):
        """重新渲染当前分数（分数变化时调用）。

        分数四舍五入到最近的 10，并使用逗号格式化（如 "12,340"）。
        位置在右上角。
        """
        rounded_score = int(round(self.stats.score, -1))
        score_str     = "{:,}".format(rounded_score)
        self.score_image = self.font.render(
            score_str, True, self.text_color, self.ai_settings.bg_color
        )
        self.score_rect       = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top   = 20

    # ─────────────────────────────────────────────────────────────────
    def prep_high_score(self):
        """重新渲染最高分（打破记录时调用）。

        位置在屏幕顶部中央，与右侧当前分数区分开。
        """
        high_score     = int(round(self.stats.high_score, -1))
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(
            high_score_str, True, self.text_color, self.ai_settings.bg_color
        )
        self.high_score_rect         = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top     = self.score_rect.top  # 与分数同一行

    # ─────────────────────────────────────────────────────────────────
    def prep_level(self):
        """重新渲染当前关卡（关卡变化时调用）。

        显示在右侧当前分数的正下方。
        """
        self.level_image = self.font.render(
            str(self.stats.level), True, self.text_color, self.ai_settings.bg_color
        )
        self.level_rect       = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top   = self.score_rect.bottom + 10  # 间隔 10 像素

    # ─────────────────────────────────────────────────────────────────
    def prep_ships(self):
        """重建生命图标组，反映剩余生命数。

        每个生命对应一个小飞船图标，从左上角开始水平排列。
        每次生命变化后调用。
        """
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship         = Ship(self.ai_settings, self.screen)
            ship.rect.x  = 10 + ship_number * ship.rect.width  # 按图标宽度排列
            ship.rect.y  = 10                                   # 距离顶部 10 像素
            self.ships.add(ship)

    # ─────────────────────────────────────────────────────────────────
    def show_score(self):
        """将所有预渲染的 HUD 表面绘制到屏幕。

        由 game_ui.update_screen() 每帧调用 —— 速度极快，
        因为只绘制已准备好的图像。
        """
        self.screen.blit(self.score_image,      self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image,      self.level_rect)
        self.ships.draw(self.screen)            # 绘制生命图标行