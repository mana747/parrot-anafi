# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import olympe
import os, csv, time, tempfile
from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged, HomeChanged
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing, moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
import olympe.enums.move as mode 

DRONE_IP = "192.168.42.1"
drone = olympe.Drone(DRONE_IP)

"""def moveto(drone, latitude, longitude, altitude, orientation_mode, heading):
    drone(moveTo(
    latitude,
    longitude,
    altitude,
    orientation_mode,
    heading
)).wait()"""
     
if __name__ == "__main__":
    drone = olympe.Drone(DRONE_IP)
    drone.connect()
    assert drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()
    assert drone(
        moveTo(drone,35.70966133333547,139.523047833378,1.0,mode.orientation_mode.to_target,0.0)
        >> moveToChanged(status=status.DONE, _timeout=10)
    ).wait().success()
    assert drone(Landing()).wait().success()
    drone.disconnect()

    
   
    