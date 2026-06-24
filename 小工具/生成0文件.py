"""
生成0文件 — 写入指定个数、指定字节大小的零数据到二进制文件

修改变量即可调整输出：
    OUTPUT_FILE — 输出的二进制文件路径
    COUNT       — 写入的数据个数
    TYPE_OR_SIZE — 数据类型 (byte/char/short/int/long/float/double 等) 或直接指定字节数
"""

from pathlib import Path

# ===== 在这里修改参数 =====
# 输出的文件名
OUTPUT_FILE = "output.bin"
# 写入到数字个数
COUNT = ((1700-1100)//50+1)*((51+9)//1+1)
# 每个数字字节数
TYPE_OR_SIZE = 4
# =========================

CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB 写块，避免大文件爆内存


def write_zeros(path: str, count: int, bytes_per_item: int) -> None:
    """向二进制文件写入 count 个 bytes_per_item 字节的零数据"""
    total_bytes = count * bytes_per_item

    out = Path(path)
    if out.exists():
        print(f"警告: 文件已存在，将被覆盖: {out}")

    print(f"输出: {out.resolve()}")
    # 自适应显示友好大小
    if total_bytes >= 1024 ** 3:
        size_str = f"{total_bytes / 1024**3:.2f} GiB"
    elif total_bytes >= 1024 ** 2:
        size_str = f"{total_bytes / 1024**2:.2f} MiB"
    elif total_bytes >= 1024:
        size_str = f"{total_bytes / 1024:.2f} KiB"
    else:
        size_str = f"{total_bytes} B"
    print(f"写入: {count} 个 × {bytes_per_item}B = {total_bytes:,} 字节 ({size_str})")

    chunk = b"\x00" * min(CHUNK_SIZE, total_bytes)

    with open(out, "wb") as f:
        written = 0
        while written < total_bytes:
            remaining = total_bytes - written
            to_write = chunk if remaining >= len(chunk) else chunk[:remaining]
            _ = f.write(to_write)
            written += len(to_write)

            # 进度提示（仅大文件时）
            if total_bytes > 100 * 1024 * 1024:  # > 100MB
                pct = written / total_bytes * 100
                print(f"\r  进度: {written:,} / {total_bytes:,} 字节 ({pct:.1f}%)", end="", flush=True)

    if total_bytes > 100 * 1024 * 1024:
        print()
    print("完成")


if __name__ == "__main__":
    write_zeros(OUTPUT_FILE, COUNT, TYPE_OR_SIZE)
