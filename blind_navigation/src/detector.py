from dataclasses import dataclass
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple
from src.config import CONFIDENCE_THRESHOLD, OBSTACLE_CLASSES

@dataclass
class Detection:
    object_name: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int
    center_x: int
    center_y: int
    width: int
    height: int

class ObjectDetector:
    def __init__(self, model_path="yolo11n.pt"):
        try:
            self.model = YOLO(model_path)
            self.is_loaded = True
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            self.is_loaded = False

    def detect(self, frame: np.ndarray, conf_thresh: float = CONFIDENCE_THRESHOLD) -> List[Detection]:
        if not self.is_loaded or frame is None:
            return []

        results = self.model(frame, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                if confidence < conf_thresh:
                    continue

                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                # Filter classes
                if class_name not in OBSTACLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                width = x2 - x1
                height = y2 - y1
                center_x = x1 + width // 2
                center_y = y1 + height // 2

                detection = Detection(
                    object_name=class_name,
                    confidence=confidence,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    center_x=center_x,
                    center_y=center_y,
                    width=width,
                    height=height
                )
                detections.append(detection)

        return detections
