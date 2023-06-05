import olympe
import os
import time
from olympe.messages.ardrone3.Piloting import TakeOff, Landing

DRONE_IP = os.environ.get("DRONE_IP", "192.168.42.1")


def test_takeoff(drone):
    drone(TakeOff()).wait().success()
    time.sleep(10)
    drone(Landing()).wait().success()
    drone.disconnect()

def takeoff(drone):
    print("------------------------------takeoff------------------------------")
    assert drone(TakeOff()).wait().success()

# 着陸
def landing(drone):
    print("------------------------------landing------------------------------")
    drone(Landing()).wait().success()
    drone.disconnect()


if __name__ == "__main__":
    # ドローン接続
    drone = olympe.Drone(DRONE_IP)
    drone.connect()
    takeoff(drone)
    time.sleep(10)
    landing(drone)
