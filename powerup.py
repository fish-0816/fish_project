"""
powerup.py — 外星人被消灭后掉落的可拾取道具胶囊。

共有三种道具类型：
  'rapid'  (金色)  — 提升子弹上限与射速，持续约6秒
  'shield' (蓝色)  — 吸收下一次伤害，不损失生命
  'multi'  (紫色)  — 每次按键发射三发散射子弹，持续约6秒

掉落行为
──────────────
道具以 powerup_speed 像素/帧的速度垂直下落。
玩家通过触碰拾取（在 game_updates.py 中使用 spritecollide 检测）。
未被拾取的道具掉出屏幕底部后会被移除。
"""

import pygame
from pygame.sprite import Sprite


class PowerUp(Sprite):
    """下落的道具胶囊精灵，带有颜色编码标签。

    类级别的字典将每种道具类型映射到对应颜色和文字标签，
    这样新增道具只需在两处各添加一行即可。
    """

    # ── 视觉配置表 ─────────────────────────────────────────
    COLORS = {
        "rapid":  (255, 215,   0),  # 金色
        "shield": ( 30, 144, 255),  # 矢车菊蓝
        "multi":  (186,  85, 211),  # 中紫色
    }
    LABELS = {
        "rapid":  "RAPID",
        "shield": "SHIELD",
        "multi":  "MULTI",
    }

    def __init__(self, ai_settings, screen, x, y, kind):
        """在 (x, y) 中心位置创建指定类型的胶囊。

        参数
        ----------
        ai_settings  提供下落速度 powerup_speed
        screen       绘制用的窗口
        x, y         生成坐标 —— 通常是被击杀外星人的中心
        kind         'rapid'、'shield'、'multi' 之一
        """
        super().__init__()
        self.screen      = screen
        self.ai_settings = ai_settings
        self.kind        = kind
        self.color       = self.COLORS[kind]

        # ── 几何尺寸 ──────────────────────────────────────────────────
        self.width, self.height = 62, 22
        # 胶囊水平居中于生成位置
        self.rect = pygame.Rect(x - self.width // 2, y, self.width, self.height)
        self.y    = float(self.rect.y)  # 浮点数位置，实现平滑下落

        # ── 标签文字 ────────────────────────────────────────────────
        # 创建时预渲染；在 update() 中每帧更新位置
        self.font      = pygame.font.SysFont(None, 19)
        self.label     = self.font.render(self.LABELS[kind], True, (255, 255, 255))
        self.label_rect = self.label.get_rect(center=self.rect.center)

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        """每帧让胶囊向下移动 powerup_speed 像素"""
        self.y         += self.ai_settings.powerup_speed
        self.rect.y     = int(self.y)
        # 让标签保持在胶囊中心
        self.label_rect.centery = self.rect.centery

    # ─────────────────────────────────────────────────────────────────
    def draw(self):
        """绘制圆角矩形胶囊与内部标签文字"""
        # 填充主体
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=5)
        # 白色1像素边框，让胶囊在任何背景下都更显眼
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 1, border_radius=5)
        # 居中标签
        self.screen.blit(self.label, self.label_rect)