"""
game_functions.py —— 三个游戏子模块的公共 API 门面。

为什么需要这个文件
──────────────────
游戏逻辑已经被拆分为三个更专注的模块：

  game_events.py   输入处理（键盘、鼠标、Play 按钮）
  game_updates.py  每帧游戏逻辑更新（移动、碰撞、计时器）
  game_ui.py       画面渲染（合成画面、HUD 覆盖层）

alien_invasion.py（主循环）只需要导入这个文件，
并通过 ``gf.some_function()`` 的方式调用函数，
因此主循环不需要知道某个函数具体属于哪个子模块。

如果以后你重构代码 —— 比如把函数移动到其他子模块、
修改函数名，或者新增函数 —— 只需要更新这里的导入列表，
项目其余部分就可以保持不变。
"""

# ── 输入 / 事件处理 ───────────────────────────────────────────────────────
from game_events import (
    stop_ship,              # 清空所有移动标志与速度
    fire_bullet,            # 生成子弹并播放射击音效
    check_keydown_events,   # 处理 KEYDOWN 按键事件并映射到游戏操作
    check_keyup_events,     # 在按键松开时清除移动标志
    check_play_button,      # 点击 Play 按钮时开始新游戏
    check_events,           # 每一帧处理 pygame 的事件队列
)

# ── 每帧游戏逻辑更新 ─────────────────────────────────────────────────────
from game_updates import (
    # 外星人舰队构建
    ship_hit,               # 处理飞船受击（护盾 / 扣命 / 游戏结束）
    get_number_aliens_x,    # 计算每一行能容纳多少外星人
    get_number_rows,        # 计算外星人可以生成多少行
    create_alien,           # 创建并放置一个外星人精灵
    create_fleet,           # 构建完整的外星人舰队

    # 每帧更新
    update_bullets,         # 更新子弹移动并检测碰撞
    check_bullet_alien_collisions,  # 处理得分、连击、粒子效果、掉落道具
    check_fleet_edges,      # 检测是否有外星人碰到左右边界
    change_fleet_direction, # 外星人舰队下移并反转方向
    check_aliens_bottom,    # 将触底外星人视为撞到飞船
    update_aliens,          # 执行完整的外星人更新流程
    check_high_score,       # 若打破最高分则更新记录

    # 新增功能更新
    update_particles,       # 推进爆炸粒子的生命周期
    update_powerups,        # 更新道具下落并检测拾取
    update_combo,           # 连击计时器倒计时，超时则重置
    update_powerup_timers,  # 道具持续时间与受击闪烁倒计时
)

# ── 画面渲染 ────────────────────────────────────────────────────────────
from game_ui import update_screen   # 合成并刷新一整帧画面