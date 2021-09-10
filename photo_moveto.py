#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from olympe.messages.camera import (
    set_camera_mode,
    set_photo_mode,
    take_photo,
    photo_progress,
)
from olympe.messages import gimbal
from olympe.messages.ardrone3.Piloting import TakeOff, Landing,moveTo
import olympe
import os
import re
import requests
import shutil
import tempfile
import xml.etree.ElementTree as ET
import time
import olympe.enums.move as mode 
from olympe.enums.ardrone3.Piloting import MoveTo_Orientation_mode
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged,moveToChanged
from olympe.enums.ardrone3.PilotingState import MoveToChanged_Status as status


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

def takeoff():
    drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()

def landing():
    drone(Landing()).wait().success()

def moveto(drone, latitude, longitude, altitude, orientation_mode, heading):
    drone(moveTo(
        latitude,
        longitude,
        altitude,
        orientation_mode,
        heading
        >> FlyingStateChanged(state="hovering", _timeout=5.0)
    )).wait()

def take_photo_burst(drone):
    # take a photo burst and get the associated media_id
    photo_saved = drone(photo_progress(result="photo_saved", _policy="wait"))
    drone(take_photo(cam_id=0)).wait()
    photo_saved.wait()
    media_id = photo_saved.received_events().last().args["media_id"]

    # download the photos associated with this media id
    media_info_response = requests.get(ANAFI_MEDIA_API_URL + media_id)
    media_info_response.raise_for_status()
    download_dir = tempfile.mkdtemp()
    for resource in media_info_response.json()["resources"]:
        image_response = requests.get(ANAFI_URL + resource["url"], stream=True)
        download_path = os.path.join(download_dir, resource["resource_id"])
        image_response.raise_for_status()
        with open(download_path, "wb") as image_file:
            shutil.copyfileobj(image_response.raw, image_file)

        # parse the xmp metadata
        with open(download_path, "rb") as image_file:
            image_data = image_file.read()
            image_xmp_start = image_data.find(b"<x:xmpmeta")
            image_xmp_end = image_data.find(b"</x:xmpmeta")
            image_xmp = ET.fromstring(image_data[image_xmp_start : image_xmp_end + 12])
            for image_meta in image_xmp[0][0]:
                xmp_tag = re.sub(r"{[^}]*}", "", image_meta.tag)
                xmp_value = image_meta.text
                # only print the XMP tags we are interested in
                if xmp_tag in XMP_TAGS_OF_INTEREST:
                    print(resource["resource_id"], xmp_tag, xmp_value)


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
            capture_interval=0.0
        )
    ).wait()


def main(drone):
    drone.connection()
    takeoff()
    moveto(drone,35.709795666666665,139.523053,3.0,MoveTo_Orientation_mode.TO_TARGET,0.0)
    set_gimbal(drone)
    time.sleep(10)
    setup_photo_burst_mode(drone)
    take_photo_burst(drone)
    landing()
    drone.disconnection()


if __name__ == "__main__":
    with olympe.Drone(ANAFI_IP) as drone:
        main(drone)