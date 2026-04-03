"""
game_ui.py — 所有绘制逻辑：屏幕合成与HUD界面叠加。

每帧绘制顺序（从后到前）
──────────────────────────────────────
  1. 背景填充（飞船受伤时显示红色闪烁）
  2. 子弹（在飞船后方，看起来像是飞船发射的）
  3. 飞船（玩家精灵）
  4. 护盾光环（激活时绘制在飞船上方）
  5. 外星人（在护盾上方，形成视觉威胁感）
  6. 道具胶囊
  7. 爆炸粒子（最上层，火花显示在所有物体上方）
  8. 计分板HUD
  9. 连击倍数标签（2倍及以上才显示）
 10. 道具状态条（左下角，仅游戏进行时显示）
 11. 暂停界面（全屏半透明遮罩+“PAUSED”文字）
 12. 开始按钮（仅标题/游戏结束界面显示）

最后只调用一次 pygame.display.flip()，
确保玩家看到完整的一帧画面，不会出现部分绘制。
"""

import pygame


# ─────────────────────────────────────────────────────────────────────────────
def update_screen(
    ai_settings, screen, stats, sb, ship, aliens, bullets,
    play_button, particles, powerups
):
    """合成并显示一帧完整画面。

    在 alien_invasion.py 的主循环中每帧调用一次，
    即使游戏暂停也会调用，确保暂停界面正常渲染。
    """

    # ── 1. 背景 ─────────────────────────────────────────────────
    # 飞船受伤后的红色闪烁期间，替换正常背景，提供强烈的视觉反馈
    if stats.hit_flash_timer > 0 and stats.game_active:
        screen.fill((255, 190, 190))    # 柔和的红色闪烁
    else:
        screen.fill(ai_settings.bg_color)

    # ── 2. 子弹 ────────────────────────────────────────────────────
    for bullet in bullets:
        bullet.draw_bullet()

    # ── 3. 飞船 ───────────────────────────────────────────────────────
    ship.blitme()

    # ── 4. 护盾光环 ────────────────────────────────────────────────
    # 比飞船稍大的蓝色圆圈，表示护盾激活
    # 绘制在飞船之后，看起来包裹着飞船
    if stats.shield_active and stats.game_active:
        radius = max(ship.rect.width, ship.rect.height) // 2 + 9
        pygame.draw.circle(screen, (30, 144, 255), ship.rect.center, radius, 3)

    # ── 5. 外星人 ─────────────────────────────────────────────────────
    aliens.draw(screen)

    # ── 6. 道具胶囊 ──────────────────────────────────────────
    for pu in powerups:
        pu.draw()

    # ── 7. 爆炸粒子 ────────────────────────────────────────
    # 最后绘制，让火花显示在外星人和子弹上方
    for particle in particles:
        particle.draw()

    # ── 8. 计分板 ─────────────────────────────────────────────────
    sb.show_score()

    # ── 9. 连击倍数标签 ─────────────────────────────────────
    # 2倍及以上才显示，避免普通状态下界面杂乱
    # 暂停时隐藏，减少视觉干扰
    if stats.combo_multiplier >= 2 and stats.game_active and not stats.game_paused:
        _draw_combo(screen, stats)

    # ── 10. 道具状态条 ───────────────────────────────────────
    # 左下角显示；每个激活的道具显示一行剩余时间百分比
    # 让玩家知道效果还能持续多久
    if stats.game_active:
        _draw_powerup_status(screen, stats, ai_settings)

    # ── 11. 暂停界面 ─────────────────────────────────────────────
    if stats.game_paused:
        _draw_pause_overlay(screen)

    # ── 12. 开始按钮 ───────────────────────────────────────────────
    if not stats.game_active:
        play_button.draw_button()

    # 将后台缓冲区内容显示到屏幕 —— 每帧只执行一次
    pygame.display.flip()


# ─────────────────────────────────────────────────────────────────────────────
def _draw_combo(screen, stats):
    """在屏幕上方居中绘制“x N COMBO!”标签。

    颜色随倍数变化：黄色（2-3倍）→ 红橙色（4-5倍），
    提升视觉刺激感。位置在计分板下方（y=58）。
    """
    font  = pygame.font.SysFont(None, 54)
    color = (255, 80, 0) if stats.combo_multiplier >= 4 else (255, 200, 0)
    img   = font.render(f"x{stats.combo_multiplier} COMBO!", True, color)
    rect  = img.get_rect(centerx=screen.get_rect().centerx, top=58)
    screen.blit(img, rect)


# ─────────────────────────────────────────────────────────────────────────────
def _draw_powerup_status(screen, stats, ai_settings):
    """在屏幕左下角绘制激活的道具状态。

    每个计时类道具显示剩余时间百分比，
    让玩家判断是否需要重新拾取。
    护盾显示“ACTIVE”，因为它没有倒计时。

    从距离底部84像素处向上堆叠，每行间距28像素，
    足够同时显示三个道具。
    """
    font = pygame.font.SysFont(None, 26)
    y    = screen.get_rect().bottom - 84    # 第一行起始位置

    if stats.shield_active:
        img = font.render("SHIELD ACTIVE", True, (30, 144, 255))
        screen.blit(img, (14, y))
        y += 28

    if stats.rapid_fire_active:
        pct = int(stats.rapid_fire_timer / ai_settings.rapid_fire_duration * 100)
        img = font.render(f"RAPID FIRE  [{pct}%]", True, (255, 215, 0))
        screen.blit(img, (14, y))
        y += 28

    if stats.multi_shot_active:
        pct = int(stats.multi_shot_timer / ai_settings.rapid_fire_duration * 100)
        img = font.render(f"MULTI SHOT  [{pct}%]", True, (186, 85, 211))
        screen.blit(img, (14, y))


# ─────────────────────────────────────────────────────────────────────────────
def _draw_pause_overlay(screen):
    """使屏幕变暗并显示“PAUSED”和继续提示。

    在当前画面上覆盖一层半透明黑色遮罩（透明度约57%），
    让玩家仍能看到暂停前的游戏状态。
    """
    # 全屏半透明深色遮罩
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 145))   # RGBA：黑色，透明度145/255
    screen.blit(overlay, (0, 0))

    # 屏幕中央大号“PAUSED”文字
    font = pygame.font.SysFont(None, 84)
    img  = font.render("PAUSED", True, (255, 255, 255))
    rect = img.get_rect(center=screen.get_rect().center)
    screen.blit(img, rect)

    # 主文字下方的小号提示文字
    hint_font = pygame.font.SysFont(None, 34)
    hint_img  = hint_font.render("Press P to continue", True, (190, 190, 190))
    hint_rect = hint_img.get_rect(
        centerx=screen.get_rect().centerx,
        top=rect.bottom + 18    # 主文字与提示之间间隔18像素
    )
    screen.blit(hint_img, hint_rect)