#!/usr/bin/python3
# Simple Glowing Ultrasonic distance test

import time
from smbus2 import SMBus, i2c_msg

I2C_BUS = 13       # <-- CHANGE THIS after you confirm which bus your sensor is on
I2C_ADDR = 0x77    # Glowing Ultrasonic default address

def read_distance_mm(bus_id=I2C_BUS, addr=I2C_ADDR):
    # Returns distance in mm (capped at 5000)
    with SMBus(bus_id) as bus:
        # Tell sensor we want a reading
        write = i2c_msg.write(addr, [0])
        bus.i2c_rdwr(write)

        # Read 2 bytes back
        read = i2c_msg.read(addr, 2)
        bus.i2c_rdwr(read)

        dist = int.from_bytes(bytes(read), byteorder="little", signed=False)
        if dist > 5000:
            dist = 5000
        return dist

if __name__ == "__main__":
    print("Glowy Ultrasonic distance test (Ctrl+C to stop)\n")

    while True:
        try:
            d_mm = read_distance_mm()
            d_cm = d_mm / 10.0
            # Filter out obviously bogus readings (0, very huge, etc.)
            if d_mm <= 0 or d_mm > 5000:
                print("No valid reading")
            else:
                print(f"Distance: {d_cm:.1f} cm  ({d_mm} mm)")
            time.sleep(0.1)

        except OSError as e:
            # This is where you'll see Errno 121 if bus/addr are wrong
            print("I2C error:", e)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopping test...")
            break
