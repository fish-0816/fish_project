Alien Invasion - 外星人入侵游戏
基于 Python 和 Pygame 开发的经典外星人入侵射击游戏
项目介绍
这是《Python 编程：从入门到实践》书中的经典项目，通过面向对象编程实现了完整的 2D 射击游戏。
玩家通过左右方向键控制飞船移动，空格键发射子弹，击落外星人群获得分数。
游戏功能
✅ 飞船左右移动
✅ 子弹发射与自动销毁
✅ 外星人群自动生成、移动、下落
✅ 子弹击中外星人计分
✅ 分数实时显示
✅ 飞船生命值限制（3 条命）
✅ 游戏失败 / 重新开始
✅ 点击 Play 按钮开始游戏
✅ 关卡提升，游戏速度加快
文件结构
plaintext
alienInvasion/
├── alien_invasion.py    # 游戏主入口
├── settings.py          # 游戏设置类
├── ship.py              # 飞船类
├── alien.py             # 外星人类
├── bullet.py            # 子弹类
├── game_stats.py        # 游戏状态统计
├── scoreboard.py        # 计分板
├── game_functions.py    # 游戏功能函数
├── button.py            # 开始按钮
├── images/              # 图片资源
│   ├── ship.bmp
│   └── alien.bmp
└── README.md            # 项目说明
运行环境
Python 3.x
Pygame
安装依赖
bash
运行
pip install pygame
运行游戏
bash
运行
python alien_invasion.py
操作说明
← → 方向键：控制飞船左右移动
空格键：发射子弹
Q 键：退出游戏
鼠标点击 Play 按钮：开始游戏
游戏规则
击毁外星人获得分数
外星人群到达屏幕底部或碰到飞船，损失一条命
3 条命用完，游戏结束
消灭所有外星人自动进入下一关，速度提升
开发说明
采用面向对象思想设计，代码结构清晰
模块化拆分：主程序、设置、精灵、函数、UI
适合 Python 初学者学习图形界面与游戏开发
作者
项目来源：Python 编程：从入门到实践
整理与完善：fish-0816
座右铭
Where fish meet, we meet
