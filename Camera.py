#!/usr/bin/env python3
# encoding:utf-8
import sys
import cv2
import time
import threading
import numpy as np
from CameraCalibration.CalibrationConfig import *

# 调用USB摄像头(call USB camera)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.cap = None
        self.width = resolution[0]
        self.height = resolution[1]
        self.frame = None
        self.opened = False
        
        #加载参数(load parameter)
        self.param_data = np.load(calibration_param_path + '.npz')
        #获取参数(get parameter)
        dim = tuple(self.param_data['dim_array'])
        k = np.array(self.param_data['k_array'].tolist())
        d = np.array(self.param_data['d_array'].tolist())
        p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim ,None).copy()
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), p, dim, cv2.CV_16SC2)
        
        self.th = threading.Thread(target=self.camera_task, args=(), daemon=True)
        self.th.start()

    def camera_open(self, correction=False):
        try:
            # Force V4L2 backend so set() works reliably
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

            # Disable automatic RGB conversion so we see the raw format
            self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

            # Try to force MJPG; if unsupported, we’ll detect raw YUV below
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            self.correction = correction
            self.opened = True

            # ---- Diagnostics ----
            fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
            fmt = "".join([chr((fourcc >> 8*i) & 0xFF) for i in range(4)])
            backend = self.cap.get(cv2.CAP_PROP_BACKEND)
            print(f"[Camera] Backend={backend}, FOURCC={fmt}, CONVERT_RGB={self.cap.get(cv2.CAP_PROP_CONVERT_RGB)}")
        except Exception as e:
            print('打开摄像头失败:', e)

    def camera_close(self):
        try:
            self.opened = False
            time.sleep(0.2)
            if self.cap is not None:
                self.cap.release()
                time.sleep(0.05)
            self.cap = None
        except Exception as e:
            print('关闭摄像头失败:', e)

    def camera_task(self):
        while True:
            try:
                if self.opened and self.cap.isOpened():
                    ret, frame_tmp = self.cap.read()
                    if not ret:
                        self.frame = None
                        time.sleep(0.01)
                        continue

                    # Shape-driven branch:
                    #   - (H, W, 2): YUV422 packed (YUYV/UYVY) -> convert to BGR
                    #   - (H, W, 3): already BGR/RGB -> just resize
                    #   - (H, W):    GREY -> convert to BGR
                    if frame_tmp.ndim == 3 and frame_tmp.shape[2] == 2:
                        # Try YUYV first, then UYVY fallback
                        try:
                            bgr = cv2.cvtColor(frame_tmp, cv2.COLOR_YUV2BGR_YUY2)
                        except cv2.error:
                            bgr = cv2.cvtColor(frame_tmp, cv2.COLOR_YUV2BGR_UYVY)
                        out = cv2.resize(bgr, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

                    elif frame_tmp.ndim == 3 and frame_tmp.shape[2] == 3:
                        # Leave as-is (GStreamer/V4L2 already produced 3-channel)
                        out = cv2.resize(frame_tmp, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

                    elif frame_tmp.ndim == 2:
                        # Grayscale → BGR
                        bgr = cv2.cvtColor(frame_tmp, cv2.COLOR_GRAY2BGR)
                        out = cv2.resize(bgr, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

                    else:
                        # Unexpected format; skip this frame
                        print(f"[Camera] Unexpected frame shape: {frame_tmp.shape}")
                        time.sleep(0.01)
                        continue

                    # Force no fisheye correction to rule it out
                    self.frame = out

                elif self.opened:
                    time.sleep(0.01)
                else:
                    time.sleep(0.01)

            except Exception as e:
                print('获取摄像头画面出错:', e)
                time.sleep(0.01)


if __name__ == '__main__':
    camera = Camera()
    camera.camera_open()
    while True:
        img = camera.frame
        if img is not None:
            cv2.imshow('img', img)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
