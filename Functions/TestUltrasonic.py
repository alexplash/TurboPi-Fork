#!/usr/bin/python3
# coding=utf8
import sys
import time

# Make sure Python can find the SDK
sys.path.append('/home/alexplash/TurboPi-Fork/')

# Import TurboPi hardware SDK
import HiwonderSDK.ros_robot_controller_sdk as rrc
import HiwonderSDK.Sonar as Sonar

# Initialize board FIRST (critical)
board = rrc.Board()

# Initialize ultrasonic sensor
sonar = Sonar.Sonar()

print("Ultrasonic Test Started (Ctrl+C to stop)\n")

while True:
    try:
        # Raw reading in millimeters
        raw = sonar.getDistance()

        # Convert to centimeters
        dist_cm = raw / 10.0

        # Filter out bogus readings
        if dist_cm <= 0 or dist_cm > 300:
            print("No valid reading")
        else:
            print(f"Distance: {dist_cm:.1f} cm")

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping ultrasonic test...")
        break
