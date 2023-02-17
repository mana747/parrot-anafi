#!/usr/bin/env python3

import asyncio
from mavsdk import System


async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyACM0:57600")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break

    #latitude = terrain_info.latitude_deg
    #longitude = terraint_info.longitude
    #print("latitude is" + latitude)
    #print("longitude is" + longitude)

    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        latitude = terrain_info.latitude_deg
        longitude = terrain_info.longitude_deg
        print("absolute_altitude is " + f'{absolute_altitude}')
        print("latitude is" + f'{latitude}')
        print("longitude is" + f'{longitude}')
        break

    print("-- Arming")
    await drone.action.arm()

    print("-- Set altitude")
    await drone.action.set_takeoff_altitude(2)

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(12)

    # To fly drone 20m above the ground plane
    flying_alt = absolute_altitude + 3.0
    # goto_location() takes Absolute MSL altitude
    await drone.action.goto_location(35.613355, 139.294781, flying_alt, 0)

    await asyncio.sleep(15)
    
    #print("-- Landing")
    #await drone.action.land()

    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(1)

    #latitude = terrain_info.latitude_deg
    #longitude = terrain_info.longitude_deg

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
