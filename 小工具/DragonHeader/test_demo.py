#!/usr/bin/env python3
"""
龙头buff检测测试工具

对任意截图执行检测，显示是否找到龙头buff及其位置。

用法:
  python test_demo.py screenshot.png              # 检测单张
  python test_demo.py screenshot.png --save       # 保存标注结果
  python test_demo.py screenshot.png --show       # 弹出窗口预览
  python test_demo.py *.png                       # 批量检测多张
  python test_demo.py folder/                     # 检测文件夹下所有png
  python test_demo.py --confidence 0.5 test.png   # 调整匹配阈值

示例:
  python test_demo.py 0.png          # 检测0.png（应该有龙头）
  python test_demo.py 0.png --save   # 检测并保存标注图
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
import logging

import cv2
import numpy as np

# 直接导入 buff_monitor 的模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from buff_monitor import TemplateMatcher, CONFIDENCE_THRESHOLD, TEMPLATE_PATH, imread, imwrite


# ================================================================
# 单图检测
# ================================================================

def check_single_image(
    matcher: TemplateMatcher,
    image_path: str,
    save_result: bool = False,
    show_result: bool = False,
) -> bool:
    """对单张截图执行龙头buff检测

    Args:
        matcher: 模板匹配器实例
        image_path: 截图路径
        save_result: 是否保存标注结果图
        show_result: 是否弹出窗口显示

    Returns:
        True=检测到龙头buff, False=未检测到
    """
    path = Path(image_path)
    if not path.exists():
        print(f'  [SKIP] 文件不存在: {image_path}')
        return False

    img = imread(str(path))
    if img is None or img.size == 0:
        print(f'  [ERR]  无法读取: {image_path}')
        return False

    h, w = img.shape[:2]
    found, conf, pos = matcher.check_image(img)

    status = 'FOUND' if found else '--'
    pos_str = f'({pos[0]},{pos[1]})' if pos else 'N/A'
    print(f'  [{status}]  {path.name:30s}  置信度={conf:.4f}  位置={pos_str}  '
          f'截图={w}x{h}')

    # 保存标注结果
    if found and save_result:
        marked = img.copy()
        if pos:
            # 在 buff 区域画框
            buff_region = matcher.crop_buff_region(img)
            bh, bw = buff_region.shape[:2]
            bx = int(w * (1 - 0.35))
            cv2.rectangle(marked, (bx, 0), (bx + bw, bh), (0, 255, 255), 1)

            # 在匹配位置画框
            ts = matcher.template.shape[1]
            cv2.rectangle(marked, pos, (pos[0] + ts, pos[1] + ts),
                          (0, 255, 0), 2)
            cv2.putText(marked, f'DragonHead conf={conf:.3f}',
                        (pos[0], pos[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        out_path = path.parent / f'{path.stem}_marked{path.suffix}'
        imwrite(str(out_path), marked)
        print(f'         -> 已保存标注: {out_path.name}')

    # 弹出窗口显示
    if show_result:
        marked = img.copy()
        if found and pos:
            ts = matcher.template.shape[1]
            cv2.rectangle(marked, pos, (pos[0] + ts, pos[1] + ts),
                          (0, 255, 0), 2)
            cv2.putText(marked, f'DragonHead {conf:.3f}',
                        (pos[0], pos[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        status_text = f'FOUND (conf={conf:.4f})' if found else 'NOT FOUND'
        cv2.putText(marked, status_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if found else (0, 0, 255), 2)

        cv2.imshow(f'Test: {path.name}', marked)
        print('  [INFO] 按任意键关闭窗口...')
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return found


# ================================================================
# 批量检测
# ================================================================

def batch_check(matcher: TemplateMatcher, paths: list[Path]) -> tuple[int, int]:
    """批量检测"""
    total = len(paths)
    found_count = 0
    for p in paths:
        if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'):
            if check_single_image(matcher, str(p)):
                found_count += 1
    return total, found_count


# ================================================================
# CLI
# ================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description='龙头buff检测测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('paths', nargs='+',
                        help='截图文件或文件夹路径（支持通配符）')
    parser.add_argument('--template', default=str(TEMPLATE_PATH),
                        help=f'模板路径 (默认: {TEMPLATE_PATH})')
    parser.add_argument('--confidence', type=float, default=CONFIDENCE_THRESHOLD,
                        help=f'匹配置信度 (默认: {CONFIDENCE_THRESHOLD})')
    parser.add_argument('--save', action='store_true',
                        help='保存标注结果图 (文件名_marked.png)')
    parser.add_argument('--show', action='store_true',
                        help='弹出OpenCV窗口显示结果')
    parser.add_argument('--debug', action='store_true',
                        help='显示详细调试日志')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # 加载模板
    template_file = Path(args.template)
    if not template_file.exists():
        print(f'ERROR: 模板不存在: {args.template}')
        print(f'请先运行: python buff_monitor.py --capture')
        return 1

    matcher = TemplateMatcher(str(template_file), args.confidence)
    print(f'模板: {template_file.name}  '
          f'{matcher.template.shape[1]}x{matcher.template.shape[0]}px  '
          f'置信度阈值={args.confidence}')
    print()

    # 展开路径
    all_paths: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f'[SKIP] 路径不存在: {p}')
            continue
        if path.is_file():
            all_paths.append(path)
        elif path.is_dir():
            all_paths.extend(path.glob('*.png'))
            all_paths.extend(path.glob('*.jpg'))
            all_paths.extend(path.glob('*.jpeg'))
            all_paths.extend(path.glob('*.bmp'))
    print(f'共 {len(all_paths)} 个截图待检测')
    print()

    # 执行检测
    found_count = 0
    for p in all_paths:
        if check_single_image(matcher, str(p), args.save, args.show):
            found_count += 1

    print()
    print(f'结果: {found_count}/{len(all_paths)} 个截图检测到龙头buff')
    return 0 if found_count > 0 else 1


if __name__ == '__main__':
    exit(main())
