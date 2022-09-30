#!usr/bin/env python
# -*- coding: utf-8 -*-
print( "dronekitスタート" )    # 開始メッセージ

from signal import signal, SIGINT   # Ctrl+C(SIGINT)の送出のために必要 
from dronekit import connect        # connectを使いたいのでインポート
from dronekit import VehicleMode    # VehicleModeも使いたいのでインポート
from dronekit import LocationGlobal, LocationGlobalRelative   # ウェイポイント移動に使いたいのでインポート
import time                         # ウェイト関数time.sleepを使うために必要

#connection_stringの生成
connection_string = "/dev/ttyACM0,115200" 

# フライトコントローラ(FC)へ接続
print( "FCへ接続: %s" % (connection_string) )    # 接続設定文字列を表示
vehicle = connect(connection_string, wait_ready=True)    # 接続

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

#    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
#    while not vehicle.is_armable:
#        print(" Waiting for vehicle to initialise...")
#        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

#高さ~mまで離陸
arm_and_takeoff(1)

#hovering5秒間
time.sleep(5)

print("Landing !")
vehicle.mode = VehicleMode("LAND")

#FCと接続を閉じる
vehicle.close()

