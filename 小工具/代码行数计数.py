import os

def count_lines_quickly(directory):
    """快速统计指定后缀文件的总行数"""
    extensions = {'.h', '.cpp', '.cc', '.c', '.hpp', '.qml'}
    total_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                    file_count += 1
                except:
                    pass
    
    return total_lines, file_count


if __name__ == "__main__":
    directory = r"F:\work\jpzx\Project\PYP\SatelliteNavigationSimulation2\src"  # 目录
    total_lines, file_count = count_lines_quickly(directory)
    print(f"找到 {file_count} 个文件")
    print(f"总行数: {total_lines}")
