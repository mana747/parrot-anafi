# -*- coding: UTF-8 -*-
#!/usr/bin/python3
from olympe.messages.camera import (
    set_camera_mode,
    set_photo_mode,
    take_photo,
    photo_progress,
)
from olympe.messages import gimbal
from olympe.messages.ardrone3.Piloting import TakeOff, Landing
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
from olympe.messages.move import extended_move_by
import olympe
import cv2
import os
import re
import csv
import requests
import shutil
import tempfile
import xml.etree.ElementTree as ET
import time
import cv2
from cv2 import aruco
import numpy as np

# Drone IP
ANAFI_IP = "192.168.42.1"
# Drone web server URL
ANAFI_URL = "http://{}/".format(ANAFI_IP)
# Drone media web API URL
ANAFI_MEDIA_API_URL = ANAFI_URL + "api/v1/media/medias/"
XMP_TAGS_OF_INTEREST = (
    "CameraRollDegree",
    "CameraPitchDegree",
    "CameraYawDegree",
    "CaptureTsUs",
    # NOTE: GPS metadata is only present if the drone has a GPS fix
    # (i.e. they won't be present indoor)
    "GPSLatitude",
    "GPSLongitude",
    "GPSAltitude",
)

### --- aruco設定 --- ###
dict_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters_create()


def takeoff(drone):
    drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()


def land(drone):
    drone(Landing()).wait().success()


def setup_photo_burst_mode(drone):
    drone(set_camera_mode(cam_id=0, value="photo")).wait()
    # For the file_format: jpeg is the only available option
    # dng is not supported in burst mode
    drone(
        set_photo_mode(
            cam_id=0,
            mode="single",
            format="rectilinear",
            file_format="jpeg",
            burst="burst_4_over_1s",
            bracketing="preset_1ev",
            capture_interval=0.0,
        )
    ).wait()


def take_photo_burst(drone):
    # take a photo burst and get the associated media_id
    photo_saved = drone(photo_progress(result="photo_saved", _policy="wait"))
    drone(take_photo(cam_id=0)).wait()
    photo_saved.wait()
    media_id = photo_saved.received_events().last().args["media_id"]

    return media_id

def save_photo(i):
    media_id = take_photo_burst(drone)
    # Save photo to local storage
    print("*******************************************************************************************************")
    print("photo_" + str(i)+".jpg")
    print("SAVING PICTURE")
    print("*******************************************************************************************************")
    media_info_response = requests.get(ANAFI_MEDIA_API_URL + media_id)
    media_info_response.raise_for_status()
    for resource in media_info_response.json()["resources"]:
        image_response = requests.get(ANAFI_URL + resource["url"])
        open("./keras-yolo3/photo/photo_"+str(i)+".jpg", 'wb').write(image_response.content)


def image_check_aruco(i):
    # 対象画像読み込み
    input_file_nm = "./keras-yolo3/photo/photo_" + str(i)+".jpg"
    input_img = cv2.imread(input_file_nm)

    # 画像の大きさを取得
    height, width, channels = input_img.shape[:3]
    print("width: " + str(width))
    print("height: " + str(height))

    gray = cv2.cvtColor(input_img, cv2.COLOR_RGB2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dict_aruco, parameters=parameters)
    # frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    # cv2.imshow('frame', frame_markers)
    list_ids = list(np.ravel(ids))
    list_ids.sort()
    print(list_ids)

    return list_ids

def set_gimbal(drone):
    drone(gimbal.set_target(
        gimbal_id=0,
        control_mode="position",
        yaw_frame_of_reference="none",   # None instead of absolute
        yaw=0.0,
        pitch_frame_of_reference="absolute",
        pitch=-90.0,
        roll_frame_of_reference="none",     # None instead of absolute
        roll=0.0,
    )).wait()


def main(drone):
    setup_photo_burst_mode(drone)
    takeoff(drone)

    for i in range(100):
        take_photo_burst(drone)
        save_photo(i)
        list_ids = image_check_aruco(i)
        if list_ids[0] == 0:
            print("**********************landing**********************")
            land(drone)
            break

    drone.disconnect()

if __name__ == "__main__":
    drone = olympe.Drone("192.168.42.1")
    drone.connect()
    main(drone)