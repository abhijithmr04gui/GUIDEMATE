import cv2
import logging
from src.config import CAMERA_INDEX

class Camera:
    def __init__(self, camera_index=CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_connected = False

    @staticmethod
    def scan_cameras(max_index=5):
        available_cameras = []
        for i in range(max_index):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        return available_cameras

    def connect(self, camera_index=None):
        if camera_index is not None:
            self.camera_index = camera_index
            
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                self.is_connected = True
                logging.info(f"CAMERA {self.camera_index} CONNECTED")
                return True
            else:
                self.is_connected = False
                logging.error(f"CAMERA {self.camera_index} NOT AVAILABLE")
                return False
        except Exception as e:
            self.is_connected = False
            logging.error(f"CAMERA NOT AVAILABLE: {e}")
            return False

    def get_frame(self):
        if not self.is_connected or self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def get_resolution(self):
        if self.is_connected and self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return 0, 0

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.is_connected = False
            logging.info("Camera released.")
