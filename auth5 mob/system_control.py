import pyautogui
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

import os
import subprocess

class SystemControl:
    def take_screenshot(self, filename="screenshot.png"):
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return filename

    def open_app(self, app_name):
        try:
            # Simple implementation for Windows
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Opening {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    def capture_camera(self, filename="camera.jpg"):
        if not HAS_CV2:
            return "Camera capture is currently unavailable (OpenCV not installed)."
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(filename, frame)
            cap.release()
            return filename
        cap.release()
        return "Failed to capture image"

    def get_screen_info(self):
        return str(pyautogui.size())
