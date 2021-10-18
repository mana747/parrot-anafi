import argparse
import cv2
import os
import sys
import time
import olympe
from olympe import Pdraw, PDRAW_YUV_FORMAT_I420, PDRAW_YUV_FORMAT_NV12, PdrawState

DRONE_IP = "192.168.42.1"


def yuv_frame_cb(yuv_frame):
    """
    This function will be called by Olympe for each decoded YUV frame.
        :type yuv_frame: olympe.Videoframe
    """
    # the Videoframe.info() dictionary contains some useful information
    # such as the video resolution
    info = yuv_frame.info()
    height, width = info["yuv"]["height"], info["yuv"]["width"]

    # yuv_frame.vmeta() returns a dictionary that contains additional
    # metadata from the drone (GPS coordinates, battery percentage, ...)

    # convert pdraw YUV flag to OpenCV YUV flag
    cv2_cvt_color_flag = {
        PDRAW_YUV_FORMAT_I420: cv2.COLOR_YUV2BGR_I420,
        PDRAW_YUV_FORMAT_NV12: cv2.COLOR_YUV2BGR_NV12,
    }[info["yuv"]["format"]]

    # yuv_frame.as_ndarray() is a 2D numpy array with the proper "shape"
    # i.e (3 * height / 2, width) because it's a YUV I420 or NV12 frame

    # Use OpenCV to convert the yuv frame to RGB
    cv2frame = cv2.cvtColor(yuv_frame.as_ndarray(), cv2_cvt_color_flag)

    f_cascade = cv2.CascadeClassifier("haarcascade_eye.xml")
    
    while (True):

        #物体認識（人）の実行
        facerect = f_cascade.detectMultiScale(cv2frame)
    
        #検出した人を囲む矩形の作成
        for rect in facerect:
            cv2.rectangle(cv2frame, tuple(rect[0:2]),tuple(rect[0:2] + rect[2:4]), (255, 255, 255), thickness=2)
        
            text = 'eye'
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(cv2frame,text,(rect[0],rect[1]-10),font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('anafi',cv2frame)

        k =  cv2.waitKey(1) & 0xFF # キー操作取得。64ビットマシンの場合,& 0xFFが必要
        prop_val = cv2.getWindowProperty("anafi", cv2.WND_PROP_ASPECT_RATIO) # ウィンドウが閉じられたかを検知する用

# qが押されるか、ウィンドウが閉じられたら終了
        if k == ord("q") or (prop_val < 0):
            break

    cv2frame.release()
    cv2.destroyAllWindows()
    


def stream(drone):
    drone.set_streaming_callbacks(raw_cb=yuv_frame_cb)
    # drone.start_video_streaming("Bee - 4773.mp4")
    drone.start_video_streaming()
    #start_t= time.time()
    # while time.time()-start_t<500:
        # print(time.time()-start_t)
        # f_handle = open("state.txt", "r")
        # print(f_handle.readline())
        # f_handle.close()

    time.sleep(1000)
    drone.stop_video_streaming()


def main(drone):
    stream(drone)
    drone.disconnection()

if __name__ == "__main__":
    drone = olympe.Drone("192.168.42.1")
    drone.connection()
    main(drone)