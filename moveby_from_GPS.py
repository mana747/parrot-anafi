
from __future__ import print_function  # python2/3 compatibility for the print function
import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveTo,moveBy,Circle, PCMD
from olympe.messages.ardrone3.PilotingState import PositionChanged
from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged
from olympe.messages.ardrone3.GPSSettingsState import HomeChanged
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged,moveToChanged
from olympe.enums.ardrone3.PilotingState import MoveToChanged_Status as status
from olympe.enums.ardrone3.Piloting import MoveTo_Orientation_mode
import olympe.enums.move as mode
import math
import os, csv, time, tempfile

start = [35.7099482, 139.5230989, 1.0]
p0 = [35.7099068, 139.5231090, 1.0]
goal = [35.709901, 139.523350, 1.0]

def get_now_gps(drone):
    # Wait for GPS fix
    drone(GPSFixStateChanged(_policy='wait'))
    return drone.get_state(HomeChanged)

def calcurate(drone,p):
    gps=get_now_gps(drone)
    print('='*10)
    lat1,log1,alt1=gps['latitude'],gps['longitude'],gps['altitude']
    lat2,log2,alt2=p[0],p[1],p[2]
    disctance=get_distance(lat1,log1,lat2,log2,8)
    direction=get_direction(lat1,log1,lat2,log2)
    x=disctance*math.cos(math.radians(direction))
    y=disctance*math.sin(math.radians(direction))
    z=0
    if x>5:
        x=5
    elif x<-5:
        x=-5
    if y>5:
        y=5
    elif y<-5:
        y=-5
    
    return x,y,z,direction

def get_distance(lat1,log1,lat2,log2,precision):
    distance=0
    if abs(lat1-lat2)<0.00001 and abs(log1-log2)<0.00001:
        distance=0
    else:
        lat1=lat1*math.pi/180
        lat2=lat2*math.pi/180
        log1=log1*math.pi/180
        log2=log2*math.pi/180
        A = 6378140
        B = 6356755
        F = (A - B) / A
        P1=math.atan((B/A)*math.tan(lat1))
        P2=math.atan((B/A)*math.tan(lat2))
        X=math.acos(math.sin(P1)*math.sin(P2)+math.cos(P1)*math.cos(P2)*math.cos(log1-log2))
        L=(F/8)*((math.sin(X)-X)*math.pow((math.sin(P1)+math.sin(P2)),2)/math.pow(math.cos(X/2),2)-(math.sin(X)-X)*math.pow(math.sin(P1)-math.sin(P2),2)/math.pow(math.sin(X),2))
        distance = A * (X + L)
        decimal_no = math.pow(10, precision)
        distance = round(decimal_no * distance / 1) / decimal_no
        return distance
def get_direction(lat1,log1,lat2,log2):
    Y = math.cos(log2 * math.pi / 180) * math.sin(lat2 * math.pi / 180 - lat1 * math.pi / 180);
    X = math.cos(log1 * math.pi / 180) * math.sin(log2 * math.pi / 180) - math.sin(log1 * math.pi / 180) * math.cos(
        log2 * math.pi / 180) * math.cos(lat2 * math.pi / 180 - lat1 * math.pi / 180)
    dirE0 = 180 * math.atan2(Y, X) / math.pi;#東向けがゼロ
    if dirE0<0:
        dirE0+=360
    dirN0=(dirE0+90)%360
    dirN0=dirN0/360*math.pi
    
    return dirN0 #北をゼロとして、角度う

def main():
    drone = olympe.Drone("192.168.42.1")
    drone.connection()
    assert drone(TakeOff()
        >> FlyingStateChanged(state="hovering", _timeout=5)).wait().success()

    x,y,z,direction=calcurate(drone,p0)
    drone(moveBy(0, 0, 0, direction)
        >> FlyingStateChanged(state="hovering", _timeout=3)).wait().success()
    
    drone(moveBy(y, x, z, 0)
        >> FlyingStateChanged(state="hovering", _timeout=3)).wait().success()
    
    print('=====================p0=====================================')
    x,y,z,direction=calcurate(drone,goal)
    drone(moveBy(0, 0, 0, direction)
  
        >> FlyingStateChanged(state="hovering", _timeout=3)).wait().success()
    drone(moveBy(y, x, z, 0)
        >> FlyingStateChanged(state="hovering", _timeout=3)).wait().success()
    
    print('=====================GOAL=====================================')
    drone(Landing()).wait()
   
    drone_gps=drone.get_state(PositionChanged)
    d=get_distance(goal[0],goal[1],drone_gps['latitude'],drone_gps['longitude'],8)
    print('===============ゴールとの差：'+d+'==========================')

if __name__ == '__main__':
    main()
