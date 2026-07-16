#!/usr/bin/env python3
"""
DragonHeader - WoW Turtle Server 1.18 龙头buff监控器

架构（三层分离）:
  TemplateMatcher  -- 纯模板匹配，可独立用于测试任意截图
  WindowCapture    -- 窗口捕获（PrintWindow进程级 + 前台提拉回退）
  DragonHeaderMonitor -- 监控循环（整合以上 + 进程管理）

测试:
  python test_demo.py screenshot.png    # 检测指定截图是否有龙头buff
"""

from __future__ import annotations

import logging
import sys
import time
import argparse
import random
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import psutil
import win32gui
import win32process
import win32api
import win32con
import win32ui
import ctypes
import subprocess
try:
    from mss import mss as MSS  # mss >= 6.0
except ImportError:
    from mss import MSS         # mss < 6.0
from mss.exception import ScreenShotError

# ================================================================
# Configuration
# ================================================================

# 需要监控的WoW进程名称 (不区分大小写)
WOW_PROCESS_NAMES: frozenset[str] = frozenset({
    'wow.exe',
    'turtlewow.exe',
    'vanilla.exe',
    'wowclassic.exe',
    'wow-64.exe',
})

# 检测间隔 (秒)
CHECK_INTERVAL: float = 1.0

# 自动跳跃间隔范围 (秒)
JUMP_MIN_INTERVAL: float = 10.0
JUMP_MAX_INTERVAL: float = 20.0

# 模板匹配置信度阈值 (0-1, 越高越严格)
CONFIDENCE_THRESHOLD: float = 0.65

# 模板图片默认路径
TEMPLATE_PATH: Path = Path(__file__).resolve().parent / 'dragon_head_buff.png'

# Buff栏搜索区域 (相对于窗口尺寸的百分比)
# 右上角 35% 宽 x 20% 高 = buff栏区域
BUFF_REGION_RIGHT: float = 0.35  # 从窗口右侧多少%
BUFF_REGION_TOP: float = 0.20    # 从窗口顶部向下多少%

# ================================================================
# Logging
# ================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s  %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('DragonHeader')


# ================================================================
# OpenCV Unicode path helpers （cv2.imread/imwrite 不支持中文路径）
# ================================================================

def imread(path: str, flags: int = cv2.IMREAD_COLOR) -> np.ndarray | None:
    """cv2.imread with Unicode path support (Windows)"""
    try:
        data = np.fromfile(path, dtype=np.uint8)
        if len(data) == 0:
            return None
        return cv2.imdecode(data, flags)
    except Exception:
        return None


def imwrite(path: str, img: np.ndarray) -> bool:
    """cv2.imwrite with Unicode path support (Windows)"""
    ext = Path(path).suffix or '.png'
    success, buf = cv2.imencode(ext, img)
    if success:
        buf.tofile(path)
        return True
    return False


# ================================================================
# Layer 1: TemplateMatcher — 纯图像处理，零依赖 Win32
# ================================================================

class TemplateMatcher:
    """模板匹配引擎

    职责:
      - 加载/保存模板图片
      - 对任意截图执行模板匹配
      - 裁剪buff区域

    可独立用于测试任意截图:
      matcher = TemplateMatcher('dragon_head_buff.png')
      result = matcher.check_image(cv2.imread('test.png'))
    """

    def __init__(self, template_path: str, confidence: float = CONFIDENCE_THRESHOLD):
        self.template = imread(template_path, cv2.IMREAD_COLOR)
        if self.template is None or self.template.size == 0:
            raise ValueError(f"无法加载模板图片: {template_path}")

        self.confidence = confidence
        log.info(f"模板: {Path(template_path).name}  "
                 f"{self.template.shape[1]}x{self.template.shape[0]}px  "
                 f"置信度阈值={confidence}")

    # ----------------------------------------------------------
    # 核心匹配
    # ----------------------------------------------------------

    def match(self, image: np.ndarray) -> tuple[bool, float, Optional[tuple[int, int]]]:
        """在给定图像中搜索模板

        Args:
            image: BGR numpy 数组

        Returns:
            (found, confidence, position)
            position = (x, y) 为匹配位置左上角，找不到时为 None
        """
        if image.size == 0:
            return False, 0.0, None

        # 模板不能比搜索图大
        if (self.template.shape[0] > image.shape[0] or
                self.template.shape[1] > image.shape[1]):
            return False, 0.0, None

        result = cv2.matchTemplate(
            image, self.template, cv2.TM_CCOEFF_NORMED,
        )
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        found = max_val >= self.confidence
        position = max_loc if found else None

        if found:
            log.debug(f"  匹配位置={max_loc} 置信度={max_val:.4f}")

        return found, max_val, position

    # ----------------------------------------------------------
    # Buff区域裁剪
    # ----------------------------------------------------------

    @staticmethod
    def crop_buff_region(
        image: np.ndarray,
        right_pct: float = BUFF_REGION_RIGHT,
        top_pct: float = BUFF_REGION_TOP,
    ) -> np.ndarray:
        """从全屏/全窗口截图中裁剪右上角buff栏区域

        Args:
            image: 全窗口截图 (BGR)
            right_pct: 从右侧多少%开始 (0.35 = 右侧35%)
            top_pct: 顶部多少%高度 (0.20 = 顶部20%)

        Returns:
            buff栏区域截图
        """
        h, w = image.shape[:2]
        bx = int(w * (1 - right_pct))
        bw = int(w * right_pct)
        bh = int(h * top_pct)
        return image[0:bh, bx:bx + bw]

    # ----------------------------------------------------------
    # 一站式检测
    # ----------------------------------------------------------

    def check_image(self, image: np.ndarray) -> tuple[bool, float, Optional[tuple[int, int]]]:
        """对全屏截图执行完整检测（裁剪buff区 → 模板匹配）

        Args:
            image: 全屏/全窗口截图

        Returns:
            (found, confidence, position_in_full_image)
        """
        buff_region = self.crop_buff_region(image)
        found, conf, pos = self.match(buff_region)
        if found and pos is not None:
            # 将位置映射回原图坐标
            h, w = image.shape[:2]
            bx = int(w * (1 - BUFF_REGION_RIGHT))
            full_pos = (bx + pos[0], pos[1])
            return found, conf, full_pos
        return found, conf, None


# ================================================================
# Layer 2: WindowCapture — Win32窗口枚举 + 进程级截图
# ================================================================

class WindowCapture:
    """窗口捕获器

    职责:
      - 枚举WoW窗口
      - 进程级截图 (PrintWindow)
      - 回退方案：前台提拉 + 屏幕截图 (mss)
    """

    def __init__(self):
        self.sct = MSS()

    # ----------------------------------------------------------
    # 窗口枚举
    # ----------------------------------------------------------

    @staticmethod
    def find_wow_windows() -> list[dict]:
        """枚举所有可见的WoW游戏窗口"""
        windows: list[dict] = []

        def enum_callback(hwnd: int, _) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                if proc.name().lower() in WOW_PROCESS_NAMES:
                    rect = win32gui.GetWindowRect(hwnd)
                    if rect[2] - rect[0] <= 0 or rect[3] - rect[1] <= 0:
                        return
                    windows.append({
                        'hwnd': hwnd,
                        'pid': pid,
                        'title': win32gui.GetWindowText(hwnd),
                        'rect': rect,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            except Exception:
                pass

        win32gui.EnumWindows(enum_callback, None)
        return windows

    # ----------------------------------------------------------
    # Path A: 进程级截图 (PrintWindow)
    # ----------------------------------------------------------

    @staticmethod
    def capture_by_hwnd(hwnd: int) -> np.ndarray | None:
        """进程级截图：PrintWindow API 直接抓取目标窗口内容

        不走屏幕合成，不改变Z序，不闪烁。
        使用 PW_RENDERFULLCONTENT 让 DWM 提供完整渲染内容。
        """
        try:
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            width = right - left
            height = bottom - top
            if width <= 0 or height <= 0:
                return None

            hwnd_dc = win32gui.GetDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            mem_dc = mfc_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            mem_dc.SelectObject(bitmap)

            # flags: PW_CLIENTONLY(1) | PW_RENDERFULLCONTENT(2) = 3
            success = ctypes.windll.user32.PrintWindow(
                hwnd, mem_dc.GetSafeHdc(), 3,
            )

            bmp_bits = bitmap.GetBitmapBits(True)
            bmp_info = bitmap.GetInfo()

            win32gui.DeleteObject(bitmap.GetHandle())
            mem_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            if not success:
                return None

            arr = np.frombuffer(bmp_bits, dtype=np.uint8).reshape(
                (bmp_info['bmHeight'], bmp_info['bmWidth'], 4),
            )
            return cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

        except Exception as e:
            log.debug(f"PrintWindow 失败 hwnd={hwnd}: {e}")
            return None

    # ----------------------------------------------------------
    # Path B (回退): 前台提拉 + 屏幕截图
    # ----------------------------------------------------------

    @staticmethod
    def _bring_to_foreground(hwnd: int) -> None:
        """强制窗口到前台（回退路径用）"""
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
            )
            try:
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)
            except Exception:
                pass
            time.sleep(0.25)
        except Exception as e:
            log.debug(f"BringToForeground 失败 hwnd={hwnd}: {e}")

    def capture_screen_region(self, region: dict) -> np.ndarray | None:
        """屏幕截图（回退用，失败返回 None）"""
        try:
            screenshot = self.sct.grab(region)
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
        except ScreenShotError as e:
            log.debug(f"屏幕截图失败: {e}")
            return None

    # ----------------------------------------------------------
    # 统一捕获接口
    # ----------------------------------------------------------

    def capture_window(
        self, hwnd: int, fallback_rect: tuple[int, int, int, int],
    ) -> np.ndarray | None:
        """捕获指定窗口的内容

        优先 PrintWindow（进程级，无闪烁），
        失败时回退到前台提拉 + 屏幕截图。

        Returns:
            BGR numpy array (全窗口内容), 或 None 如果完全无法捕获
        """
        # Path A: 进程级
        img = self.capture_by_hwnd(hwnd)
        if img is not None:
            return img

        # Path B: 回退
        log.debug(f"PrintWindow 无效，回退到前台截图 hwnd={hwnd}")
        self._bring_to_foreground(hwnd)
        try:
            rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            rect = fallback_rect

        x, y, right, bottom = rect
        w, h = right - x, bottom - y
        if w <= 0 or h <= 0:
            return None

        return self.capture_screen_region({
            'left': x, 'top': y, 'width': w, 'height': h,
        })


# ================================================================
# Layer 3: ProcessManager — 进程管理
# ================================================================

class ProcessManager:
    """进程管理器"""

    @staticmethod
    def kill(pid: int) -> bool:
        """终止进程（terminate → kill → taskkill 递进）"""
        proc_name = f"PID={pid}"

        # --- Step 1: psutil terminate ---
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.terminate()
            proc.wait(timeout=5)
            log.info(f"已关闭 {proc_name} (PID={pid})")
            return True
        except psutil.NoSuchProcess:
            return True
        except psutil.TimeoutExpired:
            log.warning(f"进程 {pid} 未响应，强制杀死...")
            try:
                proc = psutil.Process(pid)
                proc.kill()
                proc.wait(timeout=3)
                log.info(f"已强制关闭 (PID={pid})")
                return True
            except psutil.NoSuchProcess:
                return True
            except Exception as e:
                log.error(f"强制关闭失败 (PID={pid}): {e}")
                return False
        except psutil.AccessDenied:
            # psutil 没有权限 — 回退到 taskkill
            pass
        except Exception as e:
            log.error(f"关闭进程 (PID={pid}) 失败: {e}")
            return False

        # --- Step 2: taskkill /F (Windows 权限提升回退) ---
        try:
            result = subprocess.run(
                ['taskkill', '/F', '/PID', str(pid)],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                log.info(f"已通过 taskkill 关闭 {proc_name} (PID={pid})")
                return True
            else:
                log.error(f"taskkill 失败 (PID={pid}): {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            log.error(f"taskkill 超时 (PID={pid})")
            return False
        except Exception as e:
            log.error(f"taskkill 异常 (PID={pid}): {e}")
            return False


# ================================================================
# Orchestrator: DragonHeaderMonitor — 整合以上三层
# ================================================================

class DragonHeaderMonitor:
    """龙头buff监控器（主控）"""

    def __init__(
        self,
        template_path: str,
        confidence: float = CONFIDENCE_THRESHOLD,
        jump_enabled: bool = True,
        jump_min: float = JUMP_MIN_INTERVAL,
        jump_max: float = JUMP_MAX_INTERVAL,
    ):
        self.matcher = TemplateMatcher(template_path, confidence)
        self.capture = WindowCapture()
        self.proc_mgr = ProcessManager()
        self._killed_pids: set[int] = set()  # 已尝试杀过的 PID，避免重复尝试
        self._jump_enabled = jump_enabled
        self._jump_min = jump_min
        self._jump_max = jump_max
        self._last_jump_time = 0.0
        self._next_jump_delay = random.uniform(jump_min, jump_max)

    # ----------------------------------------------------------
    # 自动跳跃 (Anti-AFK)
    # ----------------------------------------------------------

    @staticmethod
    def _send_space(hwnd: int) -> None:
        """发送空格键给WoW窗口（通过PostMessage，无需前台）"""
        try:
            # VK_SPACE = 0x20, scan code = 0x39
            lparam_down = 1 | (0x39 << 16)  # repeat=1, scan=0x39
            lparam_up = 1 | (0x39 << 16) | (1 << 31)  # + key up flag
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, lparam_down)
            time.sleep(0.02)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, lparam_up)
            log.debug(f"跳跃 (hwnd={hwnd})")
        except Exception as e:
            log.debug(f"发送空格失败 hwnd={hwnd}: {e}")

    # ----------------------------------------------------------
    # 单窗口检测
    # ----------------------------------------------------------

    def check_window(self, win_info: dict) -> tuple[bool, float, np.ndarray | None]:
        """检测单个窗口是否有龙头buff

        Args:
            win_info: find_wow_windows() 返回的窗口信息

        Returns:
            (found, confidence, window_screenshot_or_None)
        """
        hwnd = win_info['hwnd']
        img = self.capture.capture_window(hwnd, win_info['rect'])
        if img is None:
            return False, 0.0, None
        found, conf, _ = self.matcher.check_image(img)
        return found, conf, img

    # ----------------------------------------------------------
    # 主循环
    # ----------------------------------------------------------

    def run(self, interval: float = CHECK_INTERVAL) -> None:
        """启动监控循环"""
        log.info('=' * 55)
        log.info('  DragonHeader 龙头buff监控器')
        log.info(f'  间隔={interval}s  置信度={self.matcher.confidence}')
        log.info(f'  模板={self.matcher.template.shape[1]}x{self.matcher.template.shape[0]}px')
        log.info(f'  进程={", ".join(sorted(WOW_PROCESS_NAMES))}')
        log.info(f'  截图=PrintWindow进程级 (失败回退前台截图)')
        if self._jump_enabled:
            log.info(f'  自动跳跃=开启 ({self._jump_min:.0f}~{self._jump_max:.0f}s)')
        else:
            log.info('  自动跳跃=关闭')
        log.info('=' * 55)

        last_no_windows_report = 0.0

        while True:
            try:
                windows = WindowCapture.find_wow_windows()

                # 清理已经不存在的 PID（进程已退出）
                active_pids = {w['pid'] for w in windows}
                self._killed_pids &= active_pids

                if not windows:
                    now = time.monotonic()
                    if now - last_no_windows_report > 10.0:
                        log.debug('未找到WoW窗口...')
                        last_no_windows_report = now
                else:
                    for win in windows:
                        pid = win['pid']
                        if pid in self._killed_pids:
                            continue  # 已经尝试杀过这个进程，跳过
                        if win['hwnd'] and win32gui.IsIconic(win['hwnd']):
                            continue

                        found, conf, _ = self.check_window(win)
                        if found:
                            log.info(
                                f"龙头buff! PID={pid} "
                                f"conf={conf:.3f} 窗口=\"{win['title']}\""
                            )
                            self.proc_mgr.kill(pid)
                            self._killed_pids.add(pid)  # 记录已尝试，避免重复

                # --- 自动跳跃 (Anti-AFK) ---
                if self._jump_enabled and windows:
                    now = time.monotonic()
                    if now - self._last_jump_time >= self._next_jump_delay:
                        for win in windows:
                            pid = win['pid']
                            if pid not in self._killed_pids:
                                self._send_space(win['hwnd'])
                                self._last_jump_time = now
                                self._next_jump_delay = random.uniform(
                                    self._jump_min, self._jump_max,
                                )
                                break

                time.sleep(interval)

            except KeyboardInterrupt:
                log.info('用户中断，退出')
                break
            except Exception as e:
                log.error(f'循环异常: {e}', exc_info=True)
                time.sleep(interval)


# ================================================================
# Template Capture Tool
# ================================================================

def capture_template_interactive() -> None:
    """交互式模板截图工具"""
    log.info('启动交互式模板截图工具')
    print()

    windows = WindowCapture.find_wow_windows()
    if not windows:
        log.error('未检测到WoW窗口！请先启动游戏。')
        sys.exit(1)

    print('检测到以下WoW窗口:')
    print('-' * 60)
    for i, win in enumerate(windows):
        rect = win['rect']
        print(f'  [{i}] PID={win["pid"]:>6d}  '
              f'{rect[2]-rect[0]}x{rect[3]-rect[1]}  '
              f'"{win["title"]}"')
    print()

    try:
        inp = input(f'请选择窗口编号 [默认=0]: ').strip()
        idx = int(inp) if inp else 0
        if idx < 0 or idx >= len(windows):
            log.error(f'无效编号，请输入 0-{len(windows)-1}')
            sys.exit(1)
    except ValueError:
        log.error('输入无效')
        sys.exit(1)

    win = windows[idx]
    log.info(f'正在截图: {win["title"]}')

    rect = win['rect']
    region = {
        'left': rect[0], 'top': rect[1],
        'width': rect[2] - rect[0],
        'height': rect[3] - rect[1],
    }

    capturer = WindowCapture()
    img = capturer.capture_screen_region(region)

    max_display_w, max_display_h = 1600, 900
    scale = 1.0
    display_img = img
    if img.shape[1] > max_display_w or img.shape[0] > max_display_h:
        scale = min(max_display_w / img.shape[1], max_display_h / img.shape[0])
        dw = int(img.shape[1] * scale)
        dh = int(img.shape[0] * scale)
        display_img = cv2.resize(img, (dw, dh), interpolation=cv2.INTER_AREA)

    print()
    print('操作: 框选龙头buff图标 → 空格确认 → Esc重来')
    print()

    cv2.namedWindow('Select Buff Icon', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Select Buff Icon',
                      min(img.shape[1], max_display_w),
                      min(img.shape[0], max_display_h))

    roi = cv2.selectROI('Select Buff Icon', display_img, False)
    cv2.destroyWindow('Select Buff Icon')

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        log.error('未选择有效区域')
        sys.exit(1)

    if scale != 1.0:
        x = int(x / scale)
        y = int(y / scale)
        w = int(w / scale)
        h = int(h / scale)

    template = img[y:y + h, x:x + w]
    print(f'\n模板尺寸: {w} x {h} px')
    confirm = input(f'保存到 {TEMPLATE_PATH.name}? [Y/n]: ').strip().lower()
    if confirm in ('', 'y', 'yes'):
        imwrite(str(TEMPLATE_PATH), template)
        log.info(f'已保存: {TEMPLATE_PATH}')
    else:
        log.info('已取消')
        sys.exit(0)

    print('按任意键关闭预览...')
    cv2.imshow('Captured Template', template)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    log.info('完成！现在可以运行 python buff_monitor.py')


# ================================================================
# CLI
# ================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description='DragonHeader - WoW Turtle Server 1.18 龙头buff监控器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""\
使用:
  python buff_monitor.py              # 启动监控
  python buff_monitor.py --capture     # 截取模板
  python buff_monitor.py --no-jump     # 关闭自动跳跃
  python buff_monitor.py --debug       # 调试模式

测试（无需游戏）:
  python test_demo.py screenshot.png   # 检测截图

模板路径: {TEMPLATE_PATH}
""",
    )
    parser.add_argument('--template', default=str(TEMPLATE_PATH))
    parser.add_argument('--confidence', type=float, default=CONFIDENCE_THRESHOLD)
    parser.add_argument('--interval', type=float, default=CHECK_INTERVAL)
    parser.add_argument('--no-jump', action='store_true', help='禁用自动跳跃')
    parser.add_argument('--jump-min', type=float, default=JUMP_MIN_INTERVAL, help='跳跃最小间隔（秒）')
    parser.add_argument('--jump-max', type=float, default=JUMP_MAX_INTERVAL, help='跳跃最大间隔（秒）')
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.capture:
        capture_template_interactive()
        return 0

    if not Path(args.template).exists():
        print()
        log.error(f'模板不存在: {args.template}')
        log.error('请先运行: python buff_monitor.py --capture')
        print()
        return 1

    try:
        monitor = DragonHeaderMonitor(
            args.template, args.confidence,
            jump_enabled=not args.no_jump,
            jump_min=args.jump_min,
            jump_max=args.jump_max,
        )
        monitor.run(args.interval)
    except Exception as e:
        log.error(f'启动失败: {e}')
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
