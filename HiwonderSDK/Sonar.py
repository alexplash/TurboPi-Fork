import sys
import time
from smbus2 import SMBus, i2c_msg

# 幻尔科技iic超声波库(Hiwonder I2C ultrasonic library)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class Sonar:
    __units = {"mm":0, "cm":1}
    __dist_reg = 0

    __RGB_MODE = 2
    __RGB1_R = 3
    __RGB1_G = 4
    __RGB1_B = 5
    __RGB2_R = 6
    __RGB2_G = 7
    __RGB2_B = 8

    __RGB1_R_BREATHING_CYCLE = 9
    __RGB1_G_BREATHING_CYCLE = 10
    __RGB1_B_BREATHING_CYCLE = 11
    __RGB2_R_BREATHING_CYCLE = 12
    __RGB2_G_BREATHING_CYCLE = 13
    __RGB2_B_BREATHING_CYCLE = 14
    def __init__(self):
        self.i2c_addr = 0x57
        self.i2c = 1
        self.Pixels = [0,0]
        self.RGBMode = 0

    def __getattr(self, attr):
        if attr in self.__units:
            return self.__units[attr]
        if attr == "Distance":
            return self.getDistance()
        else:
            raise AttributeError('Unknow attribute : %s'%attr)

    def setRGBMode(self, mode):
        try:
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, self.__RGB_MODE, mode)
        except BaseException as e:
            print(e)

    def show(self): #占位，与扩展板RGB保持调用一致(occupied, consistent with the call to the expansion board RGB)
        pass

    def numPixels(self):
        return 2

    def setPixelColor(self, index, rgb):
        color = (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
        try:
            if index != 0 and index != 1:
                return 
            start_reg = 3 if index == 0 else 6
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg, 0xFF & (color >> 16))
                bus.write_byte_data(self.i2c_addr, start_reg+1, 0xFF & (color >> 8))
                bus.write_byte_data(self.i2c_addr, start_reg+2, 0xFF & color)
                self.Pixels[index] = color
        except BaseException as e:
            print(e)

    def getPixelColor(self, index):
        if index != 0 and index != 1:
            raise ValueError("Invalid pixel index", index)
        return ((self.Pixels[index] >> 16) & 0xFF,
                (self.Pixels[index] >> 8) & 0xFF,
                self.Pixels[index] & 0xFF)

    def setBreathCycle(self, index, rgb, cycle):
        try:
            if index != 0 and index != 1:
                return
            if rgb < 0 or rgb > 2:
                return
            start_reg = 9 if index == 0 else 12
            cycle = int(cycle / 100)
            with SMBus(self.i2c) as bus:
                bus.write_byte_data(self.i2c_addr, start_reg + rgb, cycle)
        except BaseException as e:
            print(e)

    def startSymphony(self):
        self.setRGBMode(1)
        self.setBreathCycle(1,0, 2000)
        self.setBreathCycle(1,1, 3300)
        self.setBreathCycle(1,2, 4700)
        self.setBreathCycle(2,0, 4600)
        self.setBreathCycle(2,1, 2000)
        self.setBreathCycle(2,2, 3400)

    def getDistance(self):
        dist = 99999

        print(f"[Sonar] getDistance() called. Bus={self.i2c}, Addr=0x{self.i2c_addr:02X}")

        try:
            with SMBus(self.i2c) as bus:
                # ---- WRITE PHASE ----
                try:
                    print("[Sonar] Sending measurement request...")
                    msg = i2c_msg.write(self.i2c_addr, [0])
                    bus.i2c_rdwr(msg)
                    print("[Sonar] Write OK.")
                except Exception as e:
                    print(f"[Sonar] ERROR during write to 0x{self.i2c_addr:02X} on bus {self.i2c}: {e}")
                    # bail early, keep 99999
                    return dist

                # ---- READ PHASE ----
                try:
                    print("[Sonar] Reading 2 bytes...")
                    read = i2c_msg.read(self.i2c_addr, 2)
                    bus.i2c_rdwr(read)
                    raw_bytes = bytes(list(read))
                    print(f"[Sonar] Raw bytes: {raw_bytes!r}")
                except Exception as e:
                    print(f"[Sonar] ERROR during read from 0x{self.i2c_addr:02X} on bus {self.i2c}: {e}")
                    return dist

                # ---- PARSE PHASE ----
                try:
                    dist = int.from_bytes(raw_bytes, byteorder='little', signed=False)
                    print(f"[Sonar] Parsed distance (mm): {dist}")
                    if dist > 5000:
                        print("[Sonar] Distance > 5000mm, clamping to 5000.")
                        dist = 5000
                except Exception as e:
                    print(f"[Sonar] ERROR parsing distance from raw bytes {raw_bytes!r}: {e}")
                    return 99999

        except Exception as e:
            # This would catch things like failing to open the bus at all
            print(f"[Sonar] FATAL: Could not open I2C bus {self.i2c}: {e}")

        print(f"[Sonar] Returning distance: {dist} mm")
        return dist


if __name__ == '__main__':
    s = Sonar()
    s.setRGBMode(0)
    s.setPixelColor(0, (0, 0, 0))
    s.setPixelColor(1, (0, 0, 0))
    s.show()
    time.sleep(0.1)
    s.setPixelColor(0, (255, 0, 0))
    s.setPixelColor(1, (255, 0, 0))
    s.show()
    time.sleep(1)
    s.setPixelColor(0, (0, 255, 0))
    s.setPixelColor(1, (0, 255, 0))
    s.show()
    time.sleep(1)
    s.setPixelColor(0, (0, 0, 255))
    s.setPixelColor(1, (0, 0, 255))
    s.show()
    time.sleep(1)
    s.startSymphony()
    while True:
        time.sleep(0.1)
        print(s.getDistance())

