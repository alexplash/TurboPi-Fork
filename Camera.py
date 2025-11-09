#!/usr/bin/env python3
# encoding:utf-8

import cv2
import time
import threading
import numpy as np

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.width, self.height = resolution
        self.cap = None
        self.frame = None
        self.opened = False

        self.th = threading.Thread(target=self._loop, daemon=True)
        self.th.start()

    def camera_open(self):
        """
        Force GStreamer to convert YUY2 -> BGR automatically.
        This bypasses ALL OpenCV conversion issues.
        """
        try:
            pipeline = (
                "v4l2src device=/dev/video0 ! "
                "video/x-raw,format=YUY2,width=640,height=480,framerate=30/1 ! "
                "videoconvert ! "
                "video/x-raw,format=BGR ! "
                "appsink drop=true max-buffers=1 sync=false"
            )

            self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

            if not self.cap.isOpened():
                raise RuntimeError("❌ Failed to open GStreamer pipeline")

            self.opened = True
            print("✅ GStreamer pipeline active — YUY2 → BGR")

        except Exception as e:
            print("❌ camera_open ERROR:", e)

    def camera_close(self):
        self.opened = False
        time.sleep(0.2)
        if self.cap is not None:
            self.cap.release()
        self.cap = None

    def _loop(self):
        while True:
            try:
                if self.opened and self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        self.frame = cv2.resize(
                            frame, (self.width, self.height),
                            interpolation=cv2.INTER_NEAREST
                        )
                    else:
                        time.sleep(0.01)
                else:
                    time.sleep(0.01)

            except Exception as e:
                print("获取摄像头画面出错:", e)
                time.sleep(0.02)


if __name__ == "__main__":
    cam = Camera()
    cam.camera_open()
    while True:
        if cam.frame is not None:
            cv2.imshow("Cam", cam.frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cam.camera_close()
    cv2.destroyAllWindows()
