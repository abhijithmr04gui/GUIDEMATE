from src.config import VERY_CLOSE_THRESHOLD, CLOSE_THRESHOLD
from src.detector import Detection
import numpy as np

def estimate_proximity(detection: Detection, frame_height: int) -> str:
    """
    PROXIMITY ESTIMATION
    Estimates proximity from bounding-box size relative to frame size.
    """
    if frame_height == 0:
        return "FAR"
        
    box_height_ratio = detection.height / frame_height
    
    if box_height_ratio > VERY_CLOSE_THRESHOLD:
        return "VERY CLOSE"
    elif box_height_ratio > CLOSE_THRESHOLD:
        return "CLOSE"
    else:
        return "FAR"

def get_zone(center_x: int, frame_width: int) -> str:
    """
    Divides the frame into 3 horizontal zones.
    """
    if frame_width == 0:
        return "CENTER"
        
    if center_x < frame_width / 3:
        return "LEFT"
    elif center_x < 2 * frame_width / 3:
        return "CENTER"
    else:
        return "RIGHT"
