import sys
sys.path.append('/home/alexplash/TurboPi-Fork/')

from HiwonderSDK.Sonar import Sonar
import time

def get_distance_cm(sonar):
    raw = sonar.getDistance()   # Hiwonder returns millimeters
    distance_cm = raw / 10.0    # convert to centimeters
    return distance_cm

if __name__ == "__main__":
    sonar = Sonar()
    
    print("Ultrasonic Test Started (Ctrl+C to stop)")
    
    while True:
        d = get_distance_cm(sonar)

        # ignore invalid readings
        if d <= 0 or d > 300:
            print("No valid reading")
        else:
            print(f"Distance: {d:.1f} cm")
        
        time.sleep(0.1)
