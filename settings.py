"""
settings.py — 《外星人入侵》游戏的统一配置中心。

所有可调整的常量都放在这里，避免在游戏逻辑代码中到处查找数值。
分为两类：
  • 静态设置  —— 在 __init__ 中一次性设置，永不改变。
  • 动态设置  —— 每局游戏开始时通过 initialize_dynamic_settings() 重置，
                  玩家清空一波外星人后会提升难度。
"""


class Settings:
    """存储游戏中所有可配置的参数。

    设计规则：此类之外不应该出现影响难度或手感的硬编码数字 ——
    全部在这里命名一个属性，让数值平衡集中管理。
    """

    def __init__(self):
        """初始化所有静态默认值，然后初始化动态值。"""

        # ── 屏幕设置 ────────────────────────────────────────────────────
        self.screen_width  = 1200           # 屏幕宽度（像素）
        self.screen_height = 800            # 屏幕高度（像素）
        self.bg_color      = (230, 230, 230)  # 浅灰色背景

        # ── 玩家飞船 ───────────────────────────────────────────────
        self.ship_limit = 3     # 每局游戏生命数（左上角图标显示）

        # ── 子弹（基础值；连射模式会覆盖部分值） ─────
        self.bullet_width    = 3            # 子弹宽度 —— 细激光效果
        self.bullet_height   = 15           # 子弹高度
        self.bullet_color    = (60, 60, 60) # 深灰色
        self.bullets_allowed = 3            # 屏幕上同时存在的最大子弹数

        # ── 外星舰队 ───────────────────────────────────────────────
        self.fleet_drop_speed = 10  # 舰队碰到屏幕边缘转向时，向下移动的像素数

        # ── 难度升级 ────────────────────────────────────────────────
        # 每清空一波外星人，通过 increase_speed() 应用
        self.speedup_scale = 1.1    # 每关所有速度乘以该值
        self.score_scale   = 1.5    # 外星人分数增长速度快于速度

        # ── 道具掉落 ────────────────────────────────────────────
        self.powerup_drop_chance = 0.22  # 每个外星人被击杀后，22% 概率掉落道具
        self.powerup_speed       = 1.3   # 道具下落速度（像素/帧）

        # ── 计时道具持续时间 ──────────────────────────────────
        # 单位：游戏帧（≈60帧/秒 → 360帧 ≈6秒）
        self.rapid_fire_duration      = 360
        self.rapid_bullets_allowed    = 8   # 连射模式下最大子弹数
        self.rapid_bullet_speed_factor = 6  # 连射子弹速度（是基础的2倍）

        # ── 连击系统 ─────────────────────────────────────────
        # 如果玩家在这么多帧内没有再次击杀，连击重置为1倍
        # 60帧/秒时，80帧 ≈1.3秒
        self.combo_timeout = 80

        # 初始化会随着游戏进程变化的数值
        self.initialize_dynamic_settings()

    # ─────────────────────────────────────────────────────────────────
    def initialize_dynamic_settings(self):
        """重置所有速度/方向/得分为第1关默认值。

        游戏开始和新游戏开始时调用。
        关卡之间不调用 —— 由 increase_speed() 处理。
        """
        self.ship_speed_factor   = 1.5  # 飞船基础移动速度
        self.bullet_speed_factor = 3    # 子弹上升速度（像素/帧）
        self.alien_speed_factor  = 0.5  # 外星人水平移动速度（像素/帧）

        # +1 → 舰队初始向右；碰到边缘改为 -1
        self.fleet_direction = 1

        # 连击倍数生效前，每个外星人的基础分数
        self.alien_points = 50

    # ─────────────────────────────────────────────────────────────────
    def increase_speed(self):
        """提升所有移动速度和外星人分数值。

        玩家消灭整队外星人时自动调用。
        分数增长比速度更快，让后期游戏更有成就感。
        """
        self.ship_speed_factor   *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor  *= self.speedup_scale

        # 转为整数，让计分板显示更干净（无小数）
        self.alien_points = int(self.alien_points * self.score_scale)