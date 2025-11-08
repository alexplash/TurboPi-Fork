#!/usr/bin/env python3
import time
from HiwonderSDK.ros_robot_controller_sdk import Board

# Servo channel IDs
PAN = 1     # left / right
TILT = 2    # up / down

# Neutral center pulse
CENTER = 1500

board = Board()
board.enable_reception()

def move(servo, pulse, duration=0.5):
    """
    servo: int (1 or 2)
    pulse: int (1000–2000)
    duration: float seconds
    """
    print(f"Moving servo {servo} → {pulse}")
    board.pwm_servo_set_position(duration, [[servo, pulse]])
    time.sleep(duration + 0.1)

def test_center():
    print("Centering servos…")
    board.pwm_servo_set_position(0.5, [[PAN, CENTER], [TILT, CENTER]])
    time.sleep(1)

def main():
    test_center()

    # try left
    move(PAN, 2000)

    # center
    move(PAN, CENTER)

    # try right
    move(PAN, 1000)

    # center
    move(PAN, CENTER)

    # up
    move(TILT, 1000)

    # center
    move(TILT, CENTER)

    # down
    move(TILT, 2000)

    # center
    move(TILT, CENTER)

    print("Done")

if __name__ == "__main__":
    main()
