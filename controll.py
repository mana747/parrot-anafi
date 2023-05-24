from matplotlib.image import imread
import torch
import cv2
import os
import numpy as np

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
from olympe.messages.move import extended_move_by, extended_move_to
from olympe.video.pdraw import Pdraw, PdrawState
from olympe.video.renderer import PdrawRenderer
import time

# parrot設定
RTSP_URL = 'rtsp://192.168.42.1/live'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
DRONE_IP = os.environ.get("DRONE_IP", "192.168.42.1")

#モデルのロード
model = torch.hub.load(r'C:\Users\manak\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs\home\manaki\awesome\yolov5','custom',path=r'C:\Users\manak\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs\home\manaki\awesome\M1\best _crack2.pt',source='local')
THICKNESS = 5
COLOR = (255, 0, 0)
print('2')

# 変数の設定
target_found = False
start_processing = False

# 離陸
def takeoff(drone):
    print("------------------------------takeoff------------------------------")
    assert drone(TakeOff()).wait().success()
    time.sleep(5)

# 毎秒0.7mでFm前進後、3秒ポーズ
def go(drone, F):
    print("------------------------------go------------------------------")
    assert drone(
        extended_move_by(F, 0, 0, 0, 0.7, 0.7, 0.7)
    ).wait().success()
    time.sleep(3)

# 毎秒0.7mでHm高度上昇
def gain_altitude(drone, H):
    print("------------------------------gain_altitude------------------------------")
    drone(
        extended_move_by(0, 0, -H, 0, 0.7, 0.7, 0.7)
    ).wait().success()
    time.sleep(3)

# 着陸
def landing(drone):
    print("------------------------------landing------------------------------")
    drone(Landing()).wait().success()
    drone.disconnect()

def frame_processing(frame):
    if not start_processing:
        return
    global target_found
    try:
        # convert frame to rgb
        cv2_convert_flag = {
            olympe.VDEF_I420: cv2.COLOR_YUV2BGR_I420,
            olympe.VDEF_NV12: cv2.COLOR_YUV2BGR_NV12
        }[frame.format()]
        gray = cv2.cvtColor(frame.as_ndarray(), cv2_convert_flag)

        #カメラ接続
        #cap = cv2.VideoCapture(RTSP_URL)
        #if not cap.isOpened():
        #    raise IOError('Cannot open webcam')
        #    print('3')

        while True:     
        # get next frame
            #ret, frame = cap.read()
        # frame = imread(’…/people.jpg’)
        # Inference
            result = model([gray]).xyxy[0]

        # take one people
            #result = None
            #for row in results:
            #    if not row[-1]:
            #    result=tuple(row.int().numpy()[:-2])

        # draw rectangle
            if result is not None:
                start_point = (result[0], result[1])
                end_point = (result[2], result[3])
                frame = cv2.rectangle(gray, result[:2], result[2:], COLOR, THICKNESS)
        

        # show the frame
            cv2.namedWindow("result", cv2.WINDOW_NORMAL)
            cv2.imshow('result', frame)

        # read escape key echap
            c = cv2.waitKey(1)
            if c == 100:
                break

        #カメラと接続解除
        #cap.release()
        cv2.destroyAllWindows()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            # cap.release()
            pass
    except KeyboardInterrupt:
        landing(drone)

if __name__ == '__main__':
    # ドローン接続
    drone = olympe.Drone(DRONE_IP)
    drone.connect()

    # カメラ起動
    pdraw = Pdraw()
    pdraw.set_callbacks(raw_cb=frame_processing)
    pdraw.play(url=RTSP_URL)

    assert pdraw.wait(PdrawState.Playing, timeout=5)
    print("**********************start**********************")












