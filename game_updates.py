"""
game_updates.py — 每帧的游戏逻辑更新：物理、碰撞、生成。

本模块负责每一帧中**改变游戏状态**的所有内容：
  • 外星舰队创建与移动
  • 子弹飞行与子弹-外星人碰撞
  • 飞船受伤（ship_hit）
  • 道具移动与拾取检测
  • 爆炸粒子生命周期
  • 连击和道具计时器倒计时

这里不处理任何屏幕绘制 —— 绘制逻辑在 game_ui.py 中。
输入处理在 game_events.py 中。
"""

import random
from time import sleep

import pygame

from alien   import Alien
from particle import Particle
from powerup  import PowerUp


# ═════════════════════════════════════════════════════════════════════════════
# 舰队创建工具函数
# ═════════════════════════════════════════════════════════════════════════════

def get_number_aliens_x(ai_settings, alien_width):
    """返回一行能容纳多少个外星人。

    左右各留一个外星人宽度的边距，外星人之间间隔一个宽度。
    """
    available_space_x = ai_settings.screen_width - 2 * alien_width
    return int(available_space_x / (2 * alien_width))


def get_number_rows(ai_settings, ship_height, alien_height):
    """返回飞船上方能容纳多少行外星人。

    顶部预留三个外星人高度作为空间，底部预留一个飞船高度。
    """
    available_space_y = ai_settings.screen_height - (3 * alien_height) - ship_height
    return int(available_space_y / (2 * alien_height))


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """创建单个外星人并加入外星人群组。

    根据列号（alien_number）和行号（row_number）计算位置，
    使网格均匀分布。
    """
    alien       = Alien(ai_settings, screen)
    alien_width = alien.rect.width

    # x：左侧边距 + 列索引 * 2倍宽度（外星人+空隙）
    alien.x      = alien_width + 2 * alien_width * alien_number
    alien.rect.x = int(alien.x)

    # y：顶部边距 + 行索引 * 2倍高度（外星人+空隙）
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number

    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """用完整的外星人网格填充 aliens 群组。

    游戏开始或玩家清空一波外星人时调用。
    网格尺寸会根据当前飞船尺寸和屏幕尺寸重新计算。
    """
    # 用临时外星人仅用于获取尺寸
    alien           = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows     = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


# ═════════════════════════════════════════════════════════════════════════════
# 飞船受伤处理
# ═════════════════════════════════════════════════════════════════════════════

def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """处理飞船被外星人撞击（碰撞或到达底部）。

    护盾流程
    ───────────
    如果护盾激活，则吸收伤害：关闭护盾、触发红色闪烁，
    直接返回，不损失生命。

    正常流程
    ───────────
    触发闪烁 → 减少生命 → 重置所有道具和连击 →
    检查游戏结束 → 如果还有生命，清空精灵、重新生成舰队、
    飞船居中、短暂暂停。
    """
    from game_events import stop_ship

    # ── 护盾吸收伤害 ─────────────────────────────────────────────
    if stats.shield_active:
        stats.shield_active  = False
        stats.hit_flash_timer = 18  # 闪烁约0.3秒（60帧下18帧）
        return                      # 不损失生命

    # ── 受到伤害 ───────────────────────────────────────────────────
    stats.hit_flash_timer = 18      # 红色背景闪烁
    stats.ships_left -= 1
    sb.prep_ships()                 # 立即刷新生命图标显示

    stop_ship(ship)                 # 冻结飞船，防止滑行穿过外星人

    # 清空所有激活的道具并重置连击 —— 新生命从头开始
    stats.shield_active       = False
    stats.rapid_fire_active   = False
    stats.rapid_fire_timer    = 0
    stats.multi_shot_active   = False
    stats.multi_shot_timer    = 0
    stats.combo_count         = 0
    stats.combo_timer         = 0
    stats.combo_multiplier    = 1

    # ── 游戏结束检查 ───────────────────────────────────────────────
    if stats.ships_left <= 0:
        stats.game_active = False
        stats.game_paused = False
        pygame.mouse.set_visible(True)  # 显示光标用于开始按钮
        pygame.mixer.stop()             # 停止所有音效
        return

    # ── 重新生成 ───────────────────────────────────────────────────
    aliens.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()
    sleep(0.5)  # 短暂暂停，让玩家感知到受伤


# ═════════════════════════════════════════════════════════════════════════════
# 子弹更新与碰撞
# ═════════════════════════════════════════════════════════════════════════════

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets, particles, powerups):
    """更新所有子弹，处理碰撞，移除越界子弹。

    越界检查覆盖三个方向：顶部、左侧、右侧
    （散弹子弹可能横向飞出屏幕）。
    """
    bullets.update()

    check_bullet_alien_collisions(
        ai_settings, screen, stats, sb, ship, aliens, bullets, particles, powerups
    )

    # 移除离开屏幕区域的子弹
    screen_right = screen.get_rect().right
    for bullet in bullets.copy():
        if (
            bullet.rect.bottom  <= 0            # 从顶部飞出
            or bullet.rect.right < 0            # 从左侧飞出（斜向子弹）
            or bullet.rect.left  > screen_right # 从右侧飞出（斜向子弹）
        ):
            bullets.remove(bullet)


def check_bullet_alien_collisions(
    ai_settings, screen, stats, sb, ship, aliens, bullets, particles, powerups
):
    """处理子弹与外星人重叠：计分、连击、粒子效果、道具掉落。

    pygame.sprite.groupcollide 返回一个字典，
    键是击中目标的子弹，值是被击中的外星人列表。
    默认同时删除子弹和外星人（True, True）。

    每次击杀处理
    ───────────────────
    每个外星人被消灭时：
      1. 刷新连击计时器（延长连击窗口）
      2. 增加连击数，乘数最高5倍
      3. 计算得分 = 基础分数 × 连击倍数
      4. 在死亡位置生成爆炸粒子
      5. 随机掉落道具（22%概率）

    清空一波外星人
    ──────────
    最后一个外星人消失时，提升游戏速度、增加关卡、生成新舰队。
    """
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for hit_aliens in collisions.values():
            for alien in hit_aliens:
                # 每次击杀都延长连击时间
                stats.combo_timer     = ai_settings.combo_timeout
                stats.combo_count    += 1
                stats.combo_multiplier = min(stats.combo_count, 5)  # 最高5倍

                # 根据当前倍数计算得分
                stats.score += ai_settings.alien_points * stats.combo_multiplier
                sb.prep_score()

                # 视觉效果：在爆炸位置生成火花粒子
                _spawn_particles(screen, particles, alien.rect.centerx, alien.rect.centery)

                # 随机掉落道具
                if random.random() < ai_settings.powerup_drop_chance:
                    kind = random.choice(["rapid", "shield", "multi"])
                    pu   = PowerUp(
                        ai_settings, screen,
                        alien.rect.centerx, alien.rect.centery, kind
                    )
                    powerups.add(pu)

        check_high_score(stats, sb)

    # ── 清空当前波次 ──────────────────────────────────────────────────
    if len(aliens) == 0:
        bullets.empty()             # 清空残留子弹
        ai_settings.increase_speed()
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings, screen, ship, aliens)


# ═════════════════════════════════════════════════════════════════════════════
# 外星舰队移动
# ═════════════════════════════════════════════════════════════════════════════

def check_fleet_edges(ai_settings, aliens):
    """如果任意外星人到达屏幕边缘，反转整个舰队方向并下移。

    只要有一个外星人碰到边缘就触发反转，使用 break 避免重复触发。
    """
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """舰队整体下移，并翻转移动方向。"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1  # 左右方向切换 +1 ↔ -1


def check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """任意外星人到达屏幕底部，视为飞船被撞击。"""
    screen_bottom = screen.get_rect().bottom
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_bottom:
            ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            break  # 一帧只触发一次


def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """执行完整外星人更新：边缘检测 → 移动 → 碰撞检测。"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()  # 每个外星人向当前方向移动一步

    # 外星人直接碰撞飞船 → 造成伤害
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)

    # 外星人到达底部 → 造成伤害
    check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)


# ═════════════════════════════════════════════════════════════════════════════
# 爆炸粒子效果
# ═════════════════════════════════════════════════════════════════════════════

def _spawn_particles(screen, particles, x, y):
    """在 (x,y) 生成10个随机速度与颜色的爆炸火花。

    每个粒子有随机速度，使爆炸效果呈自然扇形，而非均匀圆形。
    """
    # 暖色调：黄、橙、浅黄、浅灰
    colors = [(255, 200, 50), (255, 110, 30), (255, 255, 140), (210, 210, 210)]

    for _ in range(10):
        vx = random.uniform(-3.2,  3.2)  # 水平扩散
        vy = random.uniform(-4.2,  0.6)  # 主要向上，少量向下
        particles.add(Particle(screen, x, y, random.choice(colors), vx, vy))


def update_particles(particles):
    """更新所有粒子一帧。

    每个粒子自己处理生命周期，到期自动调用 self.kill()，
    因此这里无需手动删除。
    """
    particles.update()


# ═════════════════════════════════════════════════════════════════════════════
# 道具拾取与计时器
# ═════════════════════════════════════════════════════════════════════════════

def _apply_powerup_effect(stats, kind, ai_settings):
    """激活拾取到的道具效果。

    'rapid'  → 开启连射模式并启动计时
    'shield' → 开启护盾（无计时，持续到受伤）
    'multi'  → 开启散弹模式并启动计时
    """
    if kind == "rapid":
        stats.rapid_fire_active = True
        stats.rapid_fire_timer  = ai_settings.rapid_fire_duration
    elif kind == "shield":
        stats.shield_active = True
    elif kind == "multi":
        stats.multi_shot_active = True
        stats.multi_shot_timer  = ai_settings.rapid_fire_duration


def update_powerups(ai_settings, screen, stats, ship, powerups):
    """移动所有道具，检测飞船拾取，移除未拾取的掉落物。"""
    powerups.update()  # 每个道具向下移动一步

    # 拾取飞船碰到的道具（自动从群组移除）
    collected = pygame.sprite.spritecollide(ship, powerups, True)
    for pu in collected:
        _apply_powerup_effect(stats, pu.kind, ai_settings)

    # 移除掉出屏幕底部的道具
    screen_bottom = screen.get_rect().bottom
    for pu in powerups.copy():
        if pu.rect.top >= screen_bottom:
            powerups.remove(pu)


def update_combo(stats):
    """倒计时连击计时器，超时则重置连击。

    每次击杀都会重置为 combo_timeout（80帧≈1.3秒）。
    如果玩家在计时结束前没有再次击杀，连击数和倍数重置为1倍。
    """
    if stats.combo_timer > 0:
        stats.combo_timer -= 1
        if stats.combo_timer == 0:
            stats.combo_count      = 0
            stats.combo_multiplier = 1


def update_powerup_timers(stats):
    """倒计时道具效果时间，到期关闭效果。

    同时倒计时受伤闪烁效果，使红色背景自动消失，
    无需在 game_ui.py 中额外处理。
    """
    if stats.rapid_fire_active:
        stats.rapid_fire_timer -= 1
        if stats.rapid_fire_timer <= 0:
            stats.rapid_fire_active = False

    if stats.multi_shot_active:
        stats.multi_shot_timer -= 1
        if stats.multi_shot_timer <= 0:
            stats.multi_shot_active = False

    # 受伤红色闪烁倒计时
    if stats.hit_flash_timer > 0:
        stats.hit_flash_timer -= 1


# ═════════════════════════════════════════════════════════════════════════════
# 计分系统
# ═════════════════════════════════════════════════════════════════════════════

def check_high_score(stats, sb):
    """更新最高分并刷新显示。"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()