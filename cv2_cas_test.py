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
   

import argparse
import cv2
import sys
import time
import os
from olympe import Pdraw, PDRAW_YUV_FORMAT_I420, PDRAW_YUV_FORMAT_NV12, PdrawState
import numpy as np


DRONE_IP = "192.168.42.1"


def yuv_frame_cb(yuv_frame):
    """
    This function will be called by Olympe for each decoded YUV frame.

        :type yuv_frame: olympe.VideoFrame
    """
    # the VideoFrame.info() dictionary contains some useful information
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
    # img=yuv_frame.as_ndarray()
    
    cv2frame = cv2.cvtColor(yuv_frame.as_ndarray(), cv2_cvt_color_flag)
    img = cv2.cvtColor(cv2frame, cv2.COLOR_RGB2GRAY)
    # Use OpenCV to show this frame
    findFace(img)
    cv2.imshow("Olympe Pdraw Example", img)
    cv2.waitKey(1)  # please OpenCV for 1 ms...

fbRange=[6200,6800]
pid=[0.4,0.4,0]
w,h=360,240
fb=0

def findFace(img):
    #shift+右クリックでパスのコピーwinとlinux
    # face_cascade_path='C:\Users\manak\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu18.04onWindows_79rhkp1fndgsc\LocalState\rootfs\home\manaki\awesome\mamoru\parrot2\haarcascade_frontalface_alt.xml'
    face_cascade_path='haarcascade_frontalface_alt.xml'
    
    #カスケードファイルが存在するか
    if os.path.isfile(face_cascade_path) is False:
        print('ファイルが存在しない')
        return 

    faceCascade=cv2.CascadeClassifier(face_cascade_path)
    # imgGray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgGray=img
    faces=faceCascade.detectMultiScale(imgGray,1.2,8)
    myFaceListC=[]
    myFaceListArea=[]
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,225),2)
        cx=x+w//2
        cy=y+h//2
        area=w*h
        myFaceListC.append([cx,cy])
        myFaceListArea.append(area)
    if len(myFaceListArea) !=0:
        i=myFaceListArea.index(max(myFaceListArea))
        return img,[myFaceListC[i],myFaceListArea[i]]
    else:return img,[[0,0],0]


def main(argv):
    parser = argparse.ArgumentParser(description="Olympe Pdraw Example")
    parser.add_argument(
        "-u",
        "--url",
        default="rtsp://192.168.42.1/live",
        help=(
            "Media resource (rtsp:// or file://) URL.\n"
            "See olympe.Pdraw.play documentation"
        ),
    )
    parser.add_argument("-m", "--media-name", default="DefaultVideo")
    args = parser.parse_args(argv)
    pdraw = Pdraw()
    pdraw.set_callbacks(raw_cb=yuv_frame_cb)
    pdraw.play(url=args.url, media_name=args.media_name)
    assert pdraw.wait(PdrawState.Playing, timeout=5)
    if args.url.endswith("/live"):
        # Let's see the live video streaming for 10 seconds
        time.sleep(100)
        pdraw.close()
        timeout = 5
    else:
        # When replaying a video, the pdraw stream will be closed automatically
        # at the end of the video
        # For this is example, this is the replayed video maximal duration:
        timeout = 90
    assert pdraw.wait(PdrawState.Closed, timeout=timeout)
    pdraw.dispose()


if __name__ == "__main__":
    main(sys.argv[1:])
