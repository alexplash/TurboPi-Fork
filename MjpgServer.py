#!/usr/bin/python

'''
    Author: Igor Maculan - n3wtron@gmail.com
    A Simple mjpg stream http server
'''

import sys

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

import cv2
import time
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from socketserver import ThreadingMixIn
from Camera import Camera

camera = Camera()
camera.camera_open()

quality = (int(cv2.IMWRITE_JPEG_QUALITY), 70)

class MJPG_Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--boundarydonotcross")
        self.end_headers()

        printed = False

        while True:
            frame = camera.frame
            if frame is None:
                time.sleep(0.01)
                continue

            # ✅ Print frame info ONCE
            if not printed:
                print("SERVER FRAME:", frame.shape, frame.dtype)
                printed = True

            # ✅ If YUYV (2-channel), convert to BGR
            if frame.ndim == 3 and frame.shape[2] == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)

            # ✅ Encode JPEG
            ret, jpg = cv2.imencode('.jpg', frame, quality)
            if not ret:
                continue

            jpg_bytes = jpg.tobytes()
            try:
                self.wfile.write(b"--boundarydonotcross\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n")
                self.wfile.write(b"Content-Length: " + str(len(jpg_bytes)).encode() + b"\r\n\r\n")
                self.wfile.write(jpg_bytes)
                self.wfile.write(b"\r\n")
            except:
                break


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def startMjpgServer():
    server = ThreadedHTTPServer(('', 8080), MJPG_Handler)
    print("✅ MJPEG server started at http://0.0.0.0:8080")
    server.serve_forever()

if __name__ == "__main__":
    startMjpgServer()