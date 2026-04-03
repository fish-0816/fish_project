"""
game_events.py —— 输入处理模块：键盘、鼠标以及 Play 按钮。

职责划分
────────
  check_events()       主入口 —— 读取 pygame 的事件队列，
                       并分发给下面的各个处理函数。

  check_keydown_events / check_keyup_events
                       将原始按键码转换为游戏行为（移动、射击、暂停、退出）。

  check_play_button()  处理鼠标点击 Play 按钮的逻辑。

  fire_bullet()        创建一个或多个子弹精灵并播放音效。

  stop_ship()          立即清空所有移动标志和速度。

所有函数只接收必要参数；本模块不直接操作屏幕，
所有渲染都通过传入的对象完成。
"""

import sys
import pygame

# ─────────────────────────────────────────────────────────────────────────────
def stop_ship(ship):
    """立即清空所有移动标志，并消除残余速度。

    在两种情况下调用：
      1. 玩家暂停游戏 —— 飞船应该立即停止。
      2. 飞船被击毁 —— 重生时必须是完全静止状态。
    """
    ship.moving_right = False
    ship.moving_left  = False
    ship.moving_up    = False
    ship.moving_down  = False

    # 清空惯性速度，避免恢复时飞船继续漂移
    if hasattr(ship, "velocity_x"):
        ship.velocity_x = 0.0
    if hasattr(ship, "velocity_y"):
        ship.velocity_y = 0.0


# ─────────────────────────────────────────────────────────────────────────────
def fire_bullet(ai_settings, screen, ship, bullets, stats, sound_manager):
    """如果未超过子弹上限，则生成子弹（或三连发）。

    子弹数量限制逻辑
    ────────────────
    普通模式     → 屏幕最多存在 bullets_allowed 颗子弹
    快速射击     → 上限提高为 rapid_bullets_allowed
    三重射击     → 每次发射三颗（左 / 中 / 右扩散）
    两者同时     → 三颗子弹且使用快速射击速度

    参数说明
    ----------
    bullets        当前子弹组，用于判断是否达到上限
    stats          用于判断是否启用了道具效果
    sound_manager  在发射后播放音效
    """
    from bullet import Bullet

    # 根据当前道具状态选择子弹上限
    cap = (
        ai_settings.rapid_bullets_allowed
        if stats.rapid_fire_active
        else ai_settings.bullets_allowed
    )

    if len(bullets) < cap:
        if stats.multi_shot_active:
            # 扇形发射：左、中、右
            for vx in (-2, 0, 2):
                b = Bullet(ai_settings, screen, ship, vx=vx)
                if stats.rapid_fire_active:
                    b.speed_factor = ai_settings.rapid_bullet_speed_factor
                bullets.add(b)
        else:
            # 单发直射
            b = Bullet(ai_settings, screen, ship)
            if stats.rapid_fire_active:
                b.speed_factor = ai_settings.rapid_bullet_speed_factor
            bullets.add(b)

        sound_manager.play_shoot()


# ─────────────────────────────────────────────────────────────────────────────
def check_keydown_events(event, ai_settings, screen, stats, ship, bullets, sound_manager):
    """响应 KEYDOWN（按下按键）事件。

    P 和 Q 键始终生效（不受游戏状态影响）。
    移动与射击只在游戏进行中且未暂停时生效，
    防止暂停期间缓存的输入在恢复时瞬间触发。
    """

    # ── 始终可用的控制 ────────────────────────────────────────────
    if event.key == pygame.K_p:
        if stats.game_active:
            stats.game_paused = not stats.game_paused
            if stats.game_paused:
                # 立即停止飞船，防止漂移
                stop_ship(ship)
        return  # 提前返回

    if event.key == pygame.K_q:
        sys.exit()

    # ── 游戏进行中的控制（暂停或未开始时忽略） ───────────────────
    if not stats.game_active or stats.game_paused:
        return

    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_UP:
        ship.moving_up = True
    elif event.key == pygame.K_DOWN:
        ship.moving_down = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets, stats, sound_manager)


# ─────────────────────────────────────────────────────────────────────────────
def check_keyup_events(event, ship):
    """在按键释放时清除对应的移动标志。"""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_UP:
        ship.moving_up = False
    elif event.key == pygame.K_DOWN:
        ship.moving_down = False


# ─────────────────────────────────────────────────────────────────────────────
def check_play_button(
    ai_settings, screen, stats, sb, play_button, ship, aliens, bullets,
    mouse_x, mouse_y, sound_manager, particles, powerups
):
    """如果点击了 Play 按钮且当前未在游戏中，则开始新游戏。

    双重判断（点击按钮 且 当前未开始游戏）可以防止：
    玩家在游戏中误点击按钮区域导致意外重开。

    重置顺序说明
    ────────────
    1. 先重置动态设置（速度、方向等）
    2. 重置 GameStats（生命、分数、道具、连击）
    3. 清空所有精灵组
    4. 创建新的外星人舰队
    5. 启动背景音乐
    """
    from game_updates import create_fleet

    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if not (button_clicked and not stats.game_active):
        return

    # 重置游戏配置为初始状态
    ai_settings.initialize_dynamic_settings()
    pygame.mouse.set_visible(False)

    # 重置所有游戏状态
    stats.reset_stats()
    stats.game_active = True
    stats.game_paused = False

    # 更新 HUD
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()

    # 清空所有精灵
    aliens.empty()
    bullets.empty()
    particles.empty()
    powerups.empty()

    stop_ship(ship)
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()
    sound_manager.play_background_music()


# ─────────────────────────────────────────────────────────────────────────────
def check_events(
    ai_settings, screen, stats, sb, play_button, ship, aliens, bullets,
    sound_manager, particles, powerups
):
    """读取 pygame 事件队列，并分发到对应处理函数。

    这是所有输入的唯一入口，
    在主循环的每一帧都会调用一次。
    """
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(
                ai_settings, screen, stats, sb, play_button, ship, aliens,
                bullets, mouse_x, mouse_y, sound_manager, particles, powerups
            )

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(
                event, ai_settings, screen, stats, ship, bullets, sound_manager
            )

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)