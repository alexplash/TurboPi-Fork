import cv2
import numpy as np

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))

ret, frame = cap.read()
cap.release()

if not ret:
    print("Failed to capture frame")
    exit()

print("Captured shape:", frame.shape)

# Save the raw bytes for analysis
np.save("raw_frame.npy", frame)
print("Saved raw_frame.npy")
