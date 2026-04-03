"""
particle.py — 外星人被消灭时产生的短暂火花特效。

游戏中每消灭一个外星人，会在其位置通过 game_updates.py 中的
_spawn_particles() 生成约 10 个粒子精灵。
每个粒子拥有随机速度，在固定帧数后通过 self.kill() 自动从精灵组中移除。

视觉表现
────────────────
  • 初始为 4×4 像素的小方块。
  • 随生命周期线性缩小至 1×1 像素。
  • 受模拟重力影响，会逐渐向下飘落（每帧 vy += 0.18）。
  • 当存在时间达到生命周期时，自动销毁并从内存移除。
"""

import pygame
from pygame.sprite import Sprite


class Particle(Sprite):
    """单个爆炸火花，包含速度、重力和逐渐缩小的尺寸。

    属性
    ----------
    x, y      浮点数坐标（亚像素精度）。
    vx, vy    速度分量（像素/帧）；vy 每帧增加（重力效果）。
    size      当前方块边长（像素），随时间缩小。
    age       已存在帧数。
    lifetime  自动销毁前的总存在帧数。
    """

    def __init__(self, screen, x, y, color, vx, vy):
        """在 (x, y) 位置创建一个带速度的火花。

        参数
        ----------
        screen  绘制用的窗口。
        x, y    生成坐标（通常是被消灭外星人的中心）。
        color   RGB 颜色元组，在 _spawn_particles 中随机选择。
        vx, vy  初始速度；vy 可为负（向上飞）。
        """
        super().__init__()
        self.screen   = screen
        self.color    = color
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = vx
        self.vy       = vy
        self.size     = 4       # 初始方块大小
        self.lifetime = 22      # 粒子存在总帧数
        self.age      = 0       # 已存在时间

        # rect 是 Sprite 类必需的，用于组管理和屏幕裁剪
        self.rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        """移动、老化、缩小，并在生命周期结束时自动销毁。

        主循环中通过 particles.update() 每帧调用一次。
        """
        # 应用速度与简单向下重力
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.18     # 重力：每帧向下加速

        self.age += 1

        # 粒子大小从 4 像素线性缩小到 1 像素
        self.size = max(1, int(4 * (1 - self.age / self.lifetime)))

        # 更新整数矩形，保证碰撞检测一致
        self.rect.update(int(self.x), int(self.y), self.size, self.size)

        # 时间到，从所有组中移除
        if self.age >= self.lifetime:
            self.kill()

    # ─────────────────────────────────────────────────────────────────
    def draw(self):
        """在当前位置和尺寸下绘制粒子方块。"""
        if self.size > 0:
            pygame.draw.rect(self.screen, self.color, self.rect)