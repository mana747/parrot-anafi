# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged

DRONE_IP = "192.168.42.1"

if __name__ == "__main__":
    drone = olympe.Drone(DRONE_IP)
    drone.connect()
    assert drone(
        TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()
    assert drone(
        moveBy(2, 1, -0.5, 3.14)
        >> FlyingStateChanged(state="hovering", _timeout=5)
    ).wait().success()
    assert drone(Landing()).wait().success()
    drone.disconnect()