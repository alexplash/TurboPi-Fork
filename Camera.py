#!/usr/bin/env python3
# encoding:utf-8
import sys, cv2, time, threading, numpy as np
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

def fourcc_to_str(f):
    return "".join([chr(int(f) >> 8*i & 0xFF) for i in range(4)])

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.cap = None
        self.width, self.height = resolution
        self.frame = None
        self.opened = False
        # Load calibration (unused if correction=False)
        data = np.load(calibration_param_path + '.npz')
        dim = tuple(data['dim_array'])
        k = np.array(data['k_array'].tolist())
        d = np.array(data['d_array'].tolist())
        p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim, None).copy()
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(
            k, d, np.eye(3), p, dim, cv2.CV_16SC2
        )
        self.correction = False
        self.th = threading.Thread(target=self.camera_task, daemon=True)
        self.th.start()

    def camera_open(self, correction=False):
        try:
            # Prefer V4L2 on Pi
            self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

            # 1) Try to get RAW YUYV with no in-driver conversion
            self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)  # return native format
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V'))
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            # Avoid color tweaks while debugging
            # self.cap.set(cv2.CAP_PROP_SATURATION, 40)

            # Report what we actually got
            got_fourcc = self.cap.get(cv2.CAP_PROP_FOURCC)
            print("FOURCC:", fourcc_to_str(got_fourcc), "CONVERT_RGB:", int(self.cap.get(cv2.CAP_PROP_CONVERT_RGB)))

            self.correction = correction
            self.opened = True
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

    def _to_bgr(self, frame):
        """Convert whatever we got into BGR sanely."""
        # If native (no convert) worked, we expect YUYV: shape (h,w,2) or (h,w)
        if frame.ndim == 2:
            # Some backends give packed YUYV as a single 2D image with width*2
            h, w = frame.shape
            if w % 2 == 0:
                frame2 = frame.reshape(h, w//2, 2)
                return cv2.cvtColor(frame2, cv2.COLOR_YUV2BGR_YUYV)
            else:
                return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        if frame.ndim == 3:
            h, w, c = frame.shape
            if c == 2:
                return cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)
            if c == 3:
                # Backend already converted. But if colors are wrong, try one quick fix: swap R/B.
                # We'll detect "psychedelic" later if needed; for now, provide both options.
                return frame  # treat as BGR
        return frame

    def camera_task(self):
        saved_one = False
        while True:
            try:
                if self.opened and self.cap.isOpened():
                    ret, frame_tmp = self.cap.read()
                    if not ret:
                        time.sleep(0.01)
                        continue

                    # Debug info
                    print("DEBUG shape/dtype:", frame_tmp.shape, frame_tmp.dtype)
                    if not saved_one:
                        cv2.imwrite("debug_raw.png", frame_tmp)
                        saved_one = True

                    bgr = self._to_bgr(frame_tmp)

                    # If it still looks wrong to you, try channel swap test:
                    # bgr = bgr[..., ::-1]  # temporarily test RGB→BGR swap

                    frame_resize = cv2.resize(bgr, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

                    if self.correction:
                        self.frame = cv2.remap(
                            frame_resize, self.map1, self.map2,
                            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
                        )
                    else:
                        self.frame = frame_resize
                else:
                    time.sleep(0.01)
            except Exception as e:
                print('获取摄像头画面出错:', e)
                time.sleep(0.01)

if __name__ == '__main__':
    camera = Camera()
    camera.camera_open(correction=False)

    while True:
        img = camera.frame
        if img is not None:
            cv2.imshow('img', img)
        key = cv2.waitKey(1)
        if key == 27:
            break

    camera.camera_close()
    cv2.destroyAllWindows()
