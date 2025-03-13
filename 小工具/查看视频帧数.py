import cv2

# 读取视频文件
video_path = R"F:\work\jpzx\Project\JP320\material\movie\test.h264.avi"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("无法打开视频文件")
else:
    # 获取视频的总帧数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频总帧数: {frame_count}")

# 释放资源
cap.release()
