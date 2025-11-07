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
        self.correction = False
        self.packing = 'YUYV'  # <— start here; press 'c' to toggle at runtime

        # Load fisheye maps (you can set correction=True later)
        data = np.load(calibration_param_path + '.npz')
        dim = tuple(data['dim_array'])
        k = np.array(data['k_array'].tolist())
        d = np.array(data['d_array'].tolist())
        p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(k, d, dim, None).copy()
        self.map1, self.map2 = cv2.fisheye.initUndistortRectifyMap(
            k, d, np.eye(3), p, dim, cv2.CV_16SC2
        )

        self.th = threading.Thread(target=self.camera_task, daemon=True)
        self.th.start()

    def camera_open(self, correction=False):
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        # Request raw packed YUV from driver
        self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y','U','Y','V'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print("FOURCC:", fourcc_to_str(self.cap.get(cv2.CAP_PROP_FOURCC)),
              "CONVERT_RGB:", int(self.cap.get(cv2.CAP_PROP_CONVERT_RGB)))

        self.correction = correction
        self.opened = True

    def camera_close(self):
        self.opened = False
        time.sleep(0.2)
        if self.cap is not None:
            self.cap.release()
            time.sleep(0.05)
        self.cap = None

    def _packed_yuv_to_bgr(self, frame_2ch):
        # frame_2ch is (H, W, 2) packed YUV
        if self.packing == 'YUYV':
            code = cv2.COLOR_YUV2BGR_YUYV
        else:  # 'UYVY'
            code = cv2.COLOR_YUV2BGR_UYVY
        return cv2.cvtColor(frame_2ch, code)

    def camera_task(self):
        saved_one = False
        while True:
            try:
                if not (self.opened and self.cap and self.cap.isOpened()):
                    time.sleep(0.01); continue

                ret, frame_tmp = self.cap.read()
                if not ret:
                    time.sleep(0.005); continue

                # Expect raw packed YUV: (H, W, 2)
                if frame_tmp.ndim == 3 and frame_tmp.shape[2] == 2:
                    bgr = self._packed_yuv_to_bgr(frame_tmp)
                elif frame_tmp.ndim == 3 and frame_tmp.shape[2] == 3:
                    # Driver ignored our request; treat as already BGR
                    bgr = frame_tmp
                else:
                    # Fallback
                    bgr = cv2.cvtColor(frame_tmp, cv2.COLOR_GRAY2BGR)

                if not saved_one:
                    cv2.imwrite("debug_converted.png", bgr)  # ✅ converted image
                    saved_one = True

                out = cv2.resize(bgr, (self.width, self.height), interpolation=cv2.INTER_NEAREST)

                if self.correction:
                    out = cv2.remap(out, self.map1, self.map2,
                                    interpolation=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_CONSTANT)

                # Overlay which packing is active (helps you see what you’re viewing)
                cv2.putText(out, f"PACKING: {self.packing}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv2.LINE_AA)

                self.frame = out

            except Exception as e:
                print('获取摄像头画面出错:', e)
                time.sleep(0.01)

if __name__ == '__main__':
    cam = Camera()
    cam.camera_open(correction=False)

    while True:
        if cam.frame is not None:
            cv2.imshow('img', cam.frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:   # ESC
            break
        if key == ord('c'):
            # Toggle packing live
            cam.packing = 'UYVY' if cam.packing == 'YUYV' else 'YUYV'
            print("Switched packing to:", cam.packing)

    cam.camera_close()
    cv2.destroyAllWindows()
