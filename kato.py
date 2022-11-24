import cv2
from cv2 import aruco
import numpy as np
import time

class MarkSearch :

    ### --- aruco設定 --- ###
    dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()
    

    def __init__(self, cameraID):
        RTSP_URL ='rtsp://192.168.42.1/live'
        self.cap = cv2.VideoCapture(RTSP_URL)

    def get_markID(self):
        """
        静止画を取得し、arucoマークのidリストを取得する
        """
        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dict_aruco, parameters=parameters)

        list_ids = np.ravel(ids)

        return list_ids

 
if __name__ == "__main__" :
    import cv2
    from cv2 import aruco
    import numpy as np
    import time

    ### --- aruco設定 --- ###
    dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()

    ### --- parameter --- ###
    cameraID = 0
    cam0_mark_search = MarkSearch(cameraID)

    try:
        while True:
            print(' ----- get_markID ----- ')
            print(cam0_mark_search.get_markID())
            time.sleep(0.5)
    except KeyboardInterrupt:
        cam0_mark_search.cap.release()