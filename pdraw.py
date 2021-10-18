# import argparse
# import cv2
# import sys
# import time
# import olympe
# from olympe import Pdraw, PDRAW_YUV_FORMAT_I420, PDRAW_YUV_FORMAT_NV12, PdrawState


# def yuv_frame_cb(yuv_frame):
#     """
#     This function will be called by Olympe for each decoded YUV frame.

#         :type yuv_frame: olympe.VideoFrame
#     """
#     # the VideoFrame.info() dictionary contains some useful information
#     # such as the video resolution
#     info = yuv_frame.info()
#     height, width = info["yuv"]["height"], info["yuv"]["width"]

#     # yuv_frame.vmeta() returns a dictionary that contains additional
#     # metadata from the drone (GPS coordinates, battery percentage, ...)

#     # convert pdraw YUV flag to OpenCV YUV flag
#     cv2_cvt_color_flag = {
#         PDRAW_YUV_FORMAT_I420: cv2.COLOR_YUV2BGR_I420,
#         PDRAW_YUV_FORMAT_NV12: cv2.COLOR_YUV2BGR_NV12,
#     }[info["yuv"]["format"]]

#     # yuv_frame.as_ndarray() is a 2D numpy array with the proper "shape"
#     # i.e (3 * height / 2, width) because it's a YUV I420 or NV12 frame

#     # Use OpenCV to convert the yuv frame to RGB
#     cv2frame = cv2.cvtColor(yuv_frame.as_ndarray(), cv2_cvt_color_flag)


#     face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#     eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#     while(True):
#         ret, frame = cv2frame.read()
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#         for (x,y,w,h) in faces:
#             frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
#             roi_gray = gray[y:y+h, x:x+w]
#             roi_color = frame[y:y+h, x:x+w]
#             eyes = eye_cascade.detectMultiScale(roi_gray)
#             for (ex,ey,ew,eh) in eyes:
#                 cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

#         cv2.imshow("frame",frame)

#         k =  cv2.waitKey(1) & 0xFF # キー操作取得。64ビットマシンの場合,& 0xFFが必要
#         prop_val = cv2.getWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO) # ウィンドウが閉じられたかを検知する用

# # qが押されるか、ウィンドウが閉じられたら終了
#         if k == ord("q") or (prop_val < 0):
#             break

#     cv2frame.release()
#     cv2.destroyAllWindows()


# def main(drone):
#     drone.set_streaming_callbacks(raw_cb=yuv_frame_cb)
#     drone.start_video_streaming()
#     time.sleep(10)
#     drone.stop_video_streaming()
   
import argparse
import cv2
import sys
import time
from olympe import Pdraw, PDRAW_YUV_FORMAT_I420, PDRAW_YUV_FORMAT_NV12, PdrawState

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
    cv2frame = cv2.cvtColor(yuv_frame.as_ndarray(), cv2_cvt_color_flag)

    # Use OpenCV to show this frame
    cv2.imshow("Olympe Pdraw Example", cv2frame)
    cv2.waitKey(1)  # please OpenCV for 1 ms...


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


# if __name__ == "__main__":
#     drone = olympe.Drone("192.168.42.1")
#     drone.connection()
#     main(drone)