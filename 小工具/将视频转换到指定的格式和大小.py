import cv2

# 输入和输出文件路径
input_video_path = r'G:\temp\vtest.avi'
output_video_path = r'G:\temp\output_video.avi'
# 指定目标尺寸
target_size = (640,512)  # 宽度, 高度

# 创建视频捕捉对象
cap = cv2.VideoCapture(input_video_path)

# 获取视频帧的属性
fourcc = cv2.VideoWriter_fourcc(*'H264')  # H.264编码
out = cv2.VideoWriter(output_video_path, fourcc,25, target_size)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 调整帧的大小
    resized_frame = cv2.resize(frame, target_size)
    # cv2.imshow('frame', resized_frame)

    # 写入调整大小后的帧到输出视频
    out.write(resized_frame)
    # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     break

# 释放资源
cap.release()
out.release()
cv2.destroyAllWindows()
