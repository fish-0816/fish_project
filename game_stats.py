"""
game_stats.py — 运行时状态，跟踪当前游戏会话的所有信息。

将可变的游戏状态与设置类分离，保持清晰的边界：
  • Settings  → "游戏的配置参数"
  • GameStats → "当前游戏会话中发生的一切"

最高分是唯一在同一次程序运行中跨游戏保留的值；
其他所有内容都会被 reset_stats() 重置。
"""


class GameStats:
    """跟踪单个游戏会话的所有运行时统计信息。

    属性按逻辑分组，方便快速查找：
        – 核心进度（分数、关卡、生命）
        – 道具状态（哪些强化已激活、剩余时间）
        – 连击系统（击杀链计数、计时、倍数）
        – 视觉效果（受伤闪烁倒计时）
        – 流程控制（游戏是否运行、是否暂停）
    """

    def __init__(self, ai_settings):
        """使用传入的设置对象初始化统计信息。

        最高分和游戏暂停状态在这里初始化（不在 reset_stats 中），
        因为它们需要跨游戏保留。
        """
        self.ai_settings = ai_settings

        # 首次初始化所有单局游戏字段
        self.reset_stats()

        # ── 跨游戏持久值 ──────────────────────────────
        # 游戏初始为未激活状态，先显示标题界面
        self.game_active = False

        # 最高分在程序运行期间一直保留；
        # 本版本未实现写入磁盘保存
        self.high_score = 0

        # 暂停标志放在这里（不在重置函数中），
        # 避免游戏中途暂停后死亡，复活时意外解除暂停
        self.game_paused = False

    # ─────────────────────────────────────────────────────────────────
    def reset_stats(self):
        """重置所有新游戏开始时需要重新初始化的值。

        在 __init__ 中调用一次，每次点击开始按钮时再次调用。
        不会修改最高分和游戏暂停状态。
        """

        # ── 核心进度 ─────────────────────────────────────────────
        self.ships_left = self.ai_settings.ship_limit  # 剩余生命数
        self.score = 0
        self.level = 1

        # ── 道具状态 ────────────────────────────────────────────
        # 每个道具都有“是否激活”布尔值和帧倒计时
        # 计时器到 0 时效果取消
        # 护盾没有计时器 —— 持续到吸收一次伤害

        self.shield_active = False          # 吸收下一次碰撞

        self.rapid_fire_active = False      # 提升子弹上限与射速
        self.rapid_fire_timer  = 0          # 剩余帧数

        self.multi_shot_active = False      # 每次按键发射三发子弹
        self.multi_shot_timer  = 0          # 剩余帧数

        # ── 连击击杀系统 ─────────────────────────────────────────
        # combo_count    – 连续击杀数（计时器未超时）
        # combo_timer    – 连击链重置前剩余帧数
        #                  每次击杀重置为 combo_timeout，每帧递减
        # combo_multiplier – 当前分数倍数（最高5倍）
        self.combo_count      = 0
        self.combo_timer      = 0
        self.combo_multiplier = 1

        # ── 视觉效果 ────────────────────────────────────────────
        # 受伤闪烁计时器每帧递减；
        # 大于0时背景变红，表示飞船受伤或护盾触发
        self.hit_flash_timer = 0