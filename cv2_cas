import argparse
import cv2
import os
import sys
import time
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

    f_cascade = cv2.CascadeClassifier('./haarcascades/haarcascade_fullbody.xml')

    while(True):

        #物体認識（人）の実行
        facerect = f_cascade.detectMultiScale(cv2frame, scaleFactor=1.2, minNeighbors=2, minSize=(1, 1))
    
        #検出した人を囲む矩形の作成
        for rect in facerect:
            cv2.rectangle(cv2frame, tuple(rect[0:2]),tuple(rect[0:2] + rect[2:4]), (255, 255, 255), thickness=2)
        
            text = 'person'
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(cv2frame,text,(rect[0],rect[1]-10),font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
    
        cv2.imshow("Olympe Pdraw Example", cv2frame)
        

        # qを押したら終了。
        k = cv2.waitKey(1)
        if k == ord('q'):
            break


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
        time.sleep(10)
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