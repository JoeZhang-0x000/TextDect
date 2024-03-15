import cv2
import sys

# 获取视频位置
video_path = sys.argv[1]

# 保存的位置
save_path = sys.argv[2]

# 打开视频文件
video = cv2.VideoCapture(video_path)

# 获取视频的帧率
fps = video.get(cv2.CAP_PROP_FPS)

# 计算每一秒需要采样的帧数
sample_rate = int(fps / 1)

# 初始化计数器
count = 0

# 逐帧读取视频
while video.isOpened():
    # 读取一帧
    ret, frame = video.read()
    
    # 检查是否读取成功
    if not ret:
        break
    
    # 每隔sample_rate帧保存一帧图像
    if count % sample_rate == 0:
        cv2.imwrite(f'{save_path}/frame_{count}.jpg', frame)
    
    # 增加计数器
    count += 1

# 释放视频对象
video.release()