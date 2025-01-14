import cv2

# 创建视频捕捉对象
cap = cv2.VideoCapture()
cap.open(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 调整帧的大小
    # frame = cv2.resize(frame,(640*512))
    cv2.imshow('frame', frame)

    # 写入调整大小后的帧到输出视频
    # out.write(resized_frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
# out.release()
cv2.destroyAllWindows()
