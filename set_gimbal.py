# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import olympe
import time
from olympe.messages import gimbal

DRONE_IP = "192.168.42.1"
def main():
    drone = olympe.Drone(DRONE_IP)
    drone.connect()

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
    
    drone.disconnect()
     
if __name__ == "__main__":
    main()
    
    
