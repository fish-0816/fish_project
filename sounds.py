"""
sounds.py — 程序生成音频：射击音效 + 环境背景音乐。

无需任何外部音频文件。所有声音在启动时通过 numpy 正弦波合成，
并存储为 pygame Sound 对象。

射击音效
───────────
频率从 900Hz 下降到 180Hz 的扫频正弦波，搭配指数衰减包络 ——
实现经典的“咻”激光音效，短促且辨识度高。

背景音乐
────────────────
三层叠加正弦波（55Hz 基波 + 两个谐波），由 0.25Hz 低频振荡器缓慢调制，
两端做淡入淡出处理，可无缝循环。
最终效果是低沉、呼吸感的太空氛围音，不会干扰游戏音效。
"""

import pygame
import numpy as np


class SoundManager:
    """生成并管理所有游戏音频。

    使用方法
    -----
    manager = SoundManager()          # 生成音效（启动约 0.5 秒）
    manager.play_background_music()   # 点击开始按钮时调用
    manager.play_shoot()              # 每次发射子弹时调用
    manager.stop_background_music()   # 游戏结束时停止
    """

    # 所有音频统一采样率 —— 标准 CD 音质
    SAMPLE_RATE = 44100

    def __init__(self):
        """初始化混音器并预生成所有音效。"""
        # buffer=512 降低延迟，让射击音效更跟手
        pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=2, buffer=512)

        self.shoot_sound = self._create_shoot_sound()
        self._setup_background_music()

    # ─────────────────────────────────────────────────────────────────
    def _create_shoot_sound(self):
        """合成短促的激光“咻”音效，使用降频正弦扫频。

        频率在 0.18 秒内从 900Hz 线性下降到 180Hz。
        指数包络（exp(-20t)）让音效干净、无爆音。

        返回可直接 play() 的 pygame.Sound 对象。
        """
        duration = 0.18                                     # 时长（秒）
        t = np.linspace(0, duration, int(self.SAMPLE_RATE * duration))

        # 瞬时频率从高到低线性变化
        freq = np.linspace(900, 180, len(t))
        wave = np.sin(2 * np.pi * freq * t)

        # 快速衰减包络，让声音自然消失
        envelope = np.exp(-t * 20)                          # 约0.15秒衰减完毕
        wave     = (wave * envelope * 32767).astype(np.int16)

        # pygame 混音器需要双声道（立体声）
        stereo_wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.set_volume(0.45)
        return sound

    # ─────────────────────────────────────────────────────────────────
    def _setup_background_music(self):
        """合成 4 秒无缝循环的太空氛围低音。

        三层正弦谐波：
          55 Hz  — 低音基础（振幅 0.30）
          110 Hz — 一次谐波，增加厚度（振幅 0.15）
          165 Hz — 二次谐波，增加光泽（振幅 0.08）

        合成波形由 0.25Hz 正弦波幅度调制，产生柔和的“呼吸”效果。

        循环边界使用 0.08 秒淡入淡出，避免循环时出现咔嗒声。
        """
        duration = 4.0                                      # 循环长度（秒）
        t = np.linspace(0, duration, int(self.SAMPLE_RATE * duration))

        # 三层谐波叠加
        base     = np.sin(2 * np.pi *  55 * t) * 0.30
        harmony1 = np.sin(2 * np.pi * 110 * t) * 0.15
        harmony2 = np.sin(2 * np.pi * 165 * t) * 0.08

        # 0.25Hz 低频振荡器，控制呼吸感（4秒一次呼吸）
        modulator = (np.sin(2 * np.pi * 0.25 * t) + 1) / 2
        wave      = (base + harmony1 + harmony2) * (0.5 + 0.5 * modulator)

        # 淡入淡出，实现完美无缝循环
        fade_len = int(self.SAMPLE_RATE * 0.08)            # 80毫秒渐变
        wave[:fade_len]  *= np.linspace(0, 1, fade_len)    # 淡入
        wave[-fade_len:] *= np.linspace(1, 0, fade_len)    # 淡出

        # 转为 16 位立体声
        pcm = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((pcm, pcm))

        self.bg_music_sound = pygame.sndarray.make_sound(stereo_wave)
        self.bg_music_sound.set_volume(0.18)  # 音量较低，不掩盖音效

    # ─────────────────────────────────────────────────────────────────
    def play_shoot(self):
        """播放一次激光音效（混音器会自动处理重叠）。"""
        self.shoot_sound.play()

    def play_background_music(self):
        """开始无限循环播放背景音乐（loops=-1）。"""
        self.bg_music_sound.play(loops=-1)

    def stop_background_music(self):
        """停止背景音乐（例如游戏结束时）。"""
        self.bg_music_sound.stop()