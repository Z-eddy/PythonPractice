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


def calculate_crc_16_xmodem(hex_string: str):
    """
    计算给定十六进制字符串的 CRC-16/XMODEM 校验码。
    - hex_string: 以字符串表示的十六进制数据（例如 "00 21 A5"）
    """
    # 按照空格拆分
    hex_values = hex_string.strip().split(' ')

    # CRC-16/XMODEM 参数
    crc = 0x0000  # 初始值
    polynomial = 0x1021  # 多项式

    for value in hex_values:
        if not value:  # 跳过空字符串
            continue
        # 将十六进制字符串转换为整数
        byte = int(value, 16)
        # 处理每个字节
        crc ^= (byte << 8)  # 将字节移到高8位
        for _ in range(8):  # 处理每一位
            if crc & 0x8000:  # 如果最高位为1
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFFFF  # 确保CRC保持在16位

    print(f"计算得到的 CRC-16/XMODEM 校验码: {crc:04X}")
    return crc


def main():
    # 指定文件路径
    file_path = R"F:\temp\temp.txt"
    with open(file_path, "r") as f:
        for line in f.readlines():
            # calculate_crc_8bit(line)
            calculate_crc_16_xmodem(line)


if __name__ == "__main__":
    main()
