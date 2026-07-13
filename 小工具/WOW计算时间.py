from datetime import datetime, timedelta


def calculate_future_times(start_time_str, interval_minutes, count):
    """
    根据起始时间、时间间隔和数量计算后续时间

    参数:
        start_time_str: 起始时间字符串，格式为"HH:MM"
        interval_minutes: 时间间隔（分钟）
        count: 需要计算的时间点数量

    返回:
        包含计算结果的字符串列表
    """
    # 将起始时间字符串转换为datetime对象
    start_time = datetime.strptime(start_time_str, "%H:%M")

    future_times = []
    for i in range(1, count + 1):
        # 计算每个时间点
        delta = timedelta(minutes=interval_minutes * i)
        future_time = start_time + delta
        # 格式化为"HH:MM"字符串
        future_time_str = future_time.strftime("%H:%M")
        future_times.append(future_time_str)

    return future_times


# 示例使用
if __name__ == "__main__":
    start_time = "22:00"
    interval = 100
    n = 20

    results = calculate_future_times(start_time, interval, n)
    for time_str in results:
        print(time_str)
