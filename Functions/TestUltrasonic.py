#!/usr/bin/python3
# coding=utf8
import sys
import time

sys.path.append('/home/alexplash/TurboPi-Fork/')

import HiwonderSDK.ros_robot_controller_sdk as rrc
import HiwonderSDK.Sonar as Sonar

board = rrc.Board()
sonar = Sonar.Sonar()

# 🔽 add this line to try bus 13 instead of 1
# sonar.i2c = 14   # or 14 if 13 doesn't work

print("Ultrasonic Test Started (Ctrl+C to stop)\n")

while True:
    try:
        raw = sonar.getDistance()   # mm
        dist_cm = raw / 10.0

        if dist_cm <= 0 or dist_cm > 500:
            print("No valid reading")
        else:
            print(f"Distance: {dist_cm:.1f} cm")

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping ultrasonic test...")
        break
