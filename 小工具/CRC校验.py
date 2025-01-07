def read_hex_from_file(file_path):
    """
    从指定的文件中读取十六进制字符串。
    文件中的内容应该是一行十六进制字符串（例如 "00 21 A5"）。
    """
    try:
        with open(file_path, 'r') as file:
            # 读取文件内容并去掉多余的空格、换行符
            hex_string = file.read().strip()
            return hex_string
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到！")
        return None


def calculate_crc_8bit(hex_string, crc_poly=0x07, init_crc=0x00):
    """
    计算给定十六进制字符串的单字节（8位）CRC 校验码。
    - hex_string: 以字符串表示的十六进制数据（例如 "00 21 A5"）
    - crc_poly: CRC 多项式，默认值为 0x07（标准 CRC-8）
    - init_crc: 初始 CRC 值，默认值为 0x00
    """
    try:
        # 将十六进制字符串转换为字节数据
        # 忽略中间的空格
        data = bytes.fromhex(hex_string.replace(" ", ""))

        crc = init_crc
        for byte in data:
            crc ^= byte  # 将数据字节与当前 CRC 异或
        crc &= 0xFF  # 保证 CRC 只保留 8 位
        return crc
    except ValueError:
        print("输入的十六进制字符串格式有误！")
        return None


def main():
    # 指定文件路径
    file_path = R"F:\Work\jpzx\project\JP320\material\test.txt"

    # 读取文件中的十六进制字符串
    hex_string = read_hex_from_file(file_path)
    if hex_string is None:
        return

    # print(f"从文件中读取的十六进制字符串: {hex_string}")

    # 计算单字节 CRC 校验值
    crc_result = calculate_crc_8bit(hex_string)
    if crc_result is not None:
        print(f"计算得到的单字节 CRC 校验码: {crc_result:02X}")  # 格式化为 2 位大写十六进制


if __name__ == "__main__":
    main()
