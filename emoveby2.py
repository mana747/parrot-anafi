# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
from olympe.messages.move import extended_move_by

DRONE_IP = "192.168.42.1"

def takeoff(drone):
    drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()

def extend_move(drone):
    drone(
        extended_move_by(5, 0, 0, 0, 5, 0, 0)
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()

def landing(drone):
    drone(Landing()).wait().success()

def main(drone):
    drone.connect()
    takeoff(drone)
    extend_move(drone)
    landing(drone) 
    drone.disconnect()

if __name__ == "__main__":
    drone = olympe.Drone(DRONE_IP)
    main(drone)
    
  