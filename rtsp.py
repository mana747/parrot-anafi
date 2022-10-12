from matplotlib.image import imread
import torch
import cv2
import os
import numpy as np

RTSP_URL ='rtsp://192.168.42.1/live'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS']='rtsp_transport;udp'
print('1')

#モデルのロード
model = torch.hub.load(r'/home/manaki/yolov5','custom',path=r'/home/manaki/yolov5/best_crack_size160.pt',source='local')
THICKNESS_rectangle = 5
THICKNESS_text = 5
COLOR_rectangle = (255, 0, 0)
COLOR_text = (0,255,0)
input_size = 320
print('2')

#カメラ接続
cap = cv2.VideoCapture(RTSP_URL)
if not cap.isOpened():
    raise IOError('Cannot open webcam')
    print('3')

while True:
# get next frame
    ret, frame = cap.read()
# frame = imread(’…/people.jpg’)
# Inference
    results = model([frame],size=input_size).xyxy[0]

# take one people
    result = None
    for row in results:
        if not row[-1]:
           result=tuple(row.int().numpy()[:-2])

# draw rectangle
    if result is not None:
        start_point = (result[0], result[1])
        end_point = (result[2], result[3])
        frame = cv2.rectangle(frame, result[:2], result[2:], COLOR_rectangle, THICKNESS_rectangle)
        cv2.putText(frame,'Crack',result[:2],cv2.FONT_HERSHEY_SIMPLEX,1,COLOR_text,THICKNESS_text)
        

# show the frame
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    cv2.imshow('result', frame)

# read escape key echap
    c = cv2.waitKey(1)
    if c == 100:
        break

#カメラと接続解除
cap.release()
cv2.destroyAllWindows()
