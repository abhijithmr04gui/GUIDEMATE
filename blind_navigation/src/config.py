# config.py

# Camera Configuration
CAMERA_INDEX = 0

# YOLO Configuration
CONFIDENCE_THRESHOLD = 0.50

# Obstacle Classes
OBSTACLE_CLASSES = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "chair",
    "bench",
    "dog",
    "cat"
}

# Distance/Proximity Thresholds
# Ratio of bounding box height to frame height
VERY_CLOSE_THRESHOLD = 0.60
CLOSE_THRESHOLD = 0.35
