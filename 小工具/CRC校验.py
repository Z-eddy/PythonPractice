def calculate_crc_8bit(hexString: str):
    """
    计算给定十六进制字符串的单字节（8位）CRC 校验码。
    - hex_string: 以字符串表示的十六进制数据（例如 "00 21 A5"）
    """
    # 按照空格拆分
    hexValues = hexString.strip().split(' ')
    # 计算的结果
    result = 0
    for value in hexValues:
        # 将十六进制字符串转换为整数
        item = int(value, 16)
        # 将数据字节与当前 CRC 异或
        result ^= item
    # 格式化为 2 位大写十六进制
    print(f"计算得到的单字节 CRC 校验码: {result:02X}")


def main():
    # 指定文件路径
    file_path = R"F:\work\jpzx\Project\29\JP103\doc\temp.txt"
    with open(file_path, "r") as f:
        for line in f.readlines():
            calculate_crc_8bit(line)


if __name__ == "__main__":
    main()
