"""
alien_invasion.py —— 游戏入口与主循环。

启动流程
────────
  1. pygame.init()          初始化 pygame 的所有子系统。
  2. Settings               加载所有配置常量。
  3. Screen                 创建游戏显示窗口。
  4. SoundManager           预生成所有音频（约 0.5 秒，只执行一次）。
  5. UI 对象                 创建 Play 按钮、记分牌等界面元素。
  6. 精灵组                  创建飞船、子弹、外星人、粒子、道具等对象组。
  7. 初始外星人舰队           在主循环开始前生成外星人编队， 这样标题界面也能显示背景中的舰队。
  8. GameStats              初始化运行时状态（分数、生命等）。

主循环（按显示器刷新频率持续运行）
────────────────────────────────
  check_events()   → 读取键盘 / 鼠标输入
  [如果游戏进行中且未暂停]
    ship.update()           应用惯性移动
    update_bullets()        更新子弹移动并检测碰撞
    update_aliens()         更新外星人移动并检测碰撞
    update_particles()      更新爆炸粒子的生命周期
    update_powerups()       更新道具下落与拾取
    update_combo()          连击计时器倒计时
    update_powerup_timers() 道具持续时间倒计时
  update_screen()  → 绘制并显示当前帧画面
"""

import pygame
from pygame.sprite import Group

from settings   import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button     import Button
from ship       import Ship
from sounds     import SoundManager
import game_functions as gf


def run_game():
    """初始化所有内容并运行游戏主循环。"""

    # ── 初始化阶段 ────────────────────────────────────────────────
    pygame.init()
    ai_settings = Settings()

    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height)
    )
    pygame.display.set_caption("Alien Invasion")

    # SoundManager 会在启动时合成所有音频，
    # 这样第一次播放音效时不会出现延迟。
    sound_manager = SoundManager()

    # ── 界面对象 ──────────────────────────────────────────────────
    play_button = Button(ai_settings, screen, "Play")

    # ── 精灵组 ───────────────────────────────────────────────────
    ship      = Ship(ai_settings, screen)
    bullets   = Group()     # 玩家发射的子弹
    aliens    = Group()     # 入侵的外星人舰队
    particles = Group()     # 外星人爆炸时产生的粒子
    powerups  = Group()     # 可拾取的掉落道具

    # 预先生成外星人舰队，使其在标题界面中也可见。
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # ── 运行时状态与 HUD ─────────────────────────────────────────
    stats = GameStats(ai_settings)
    sb    = Scoreboard(ai_settings, screen, stats)

    # ── 主循环 ───────────────────────────────────────────────────
    while True:
        # 1. 处理本帧中所有排队等待的输入事件。
        gf.check_events(
            ai_settings, screen, stats, sb, play_button,
            ship, aliens, bullets, sound_manager, particles, powerups
        )

        # 2. 推进游戏状态 —— 仅在游戏开始且未暂停时执行。
        if stats.game_active and not stats.game_paused:
            ship.update()   # 应用惯性移动，并限制在屏幕范围内

            gf.update_bullets(
                ai_settings, screen, stats, sb, ship, aliens, bullets,
                particles, powerups
            )
            gf.update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets)
            gf.update_particles(particles)
            gf.update_powerups(ai_settings, screen, stats, ship, powerups)
            gf.update_combo(stats)
            gf.update_powerup_timers(stats)

        # 3. 渲染完整的一帧画面（即使暂停时也会执行，
        #    这样暂停遮罩层仍然可以正常显示）。
        gf.update_screen(
            ai_settings, screen, stats, sb, ship, aliens, bullets,
            play_button, particles, powerups
        )


# 这个保护判断确保：
# 只有直接运行本文件时才会执行 run_game()，
# 如果它被其他模块导入，则不会自动启动游戏。
if __name__ == "__main__":
    run_game()