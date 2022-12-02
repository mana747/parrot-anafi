#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import olympe
import os, csv, time, tempfile 
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged,MoveToChanged
from olympe.enums.ardrone3.Piloting import MoveTo_Orientation_mode


DRONE_IP = "192.168.42.1"
drone = olympe.Drone(DRONE_IP)
     
def takeoff(drone):
    drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()

def moveto(drone):
    drone(
        moveTo(35.709795666666665,139.523053,3.0,MoveTo_Orientation_mode.TO_TARGET,0.0)
        >> MoveToChanged(status = "DONE", _timeout=10)
    ).wait().success()

def landing(drone):
    drone(Landing()).wait().success()

def main(drone):
    drone.connect()
    takeoff(drone)
    moveto(drone)
    landing(drone) 
    drone.disconnect()

if __name__ == "__main__":
    drone = olympe.Drone(DRONE_IP)
    main(drone)

