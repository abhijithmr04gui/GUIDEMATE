# Blind Navigation System

## Objective
This is a real-time proof-of-concept for a blind-assistance navigation system. The prototype uses a MacBook camera and a YOLO object-detection model (`yolo11n.pt`) to detect obstacles in real time and generate navigation commands (FORWARD, MOVE LEFT, MOVE RIGHT, STOP).

## Architecture

```text
MacBook Camera
      ↓
YOLO Object Detection
      ↓
Detection (Class, Confidence, Bounding Box)
      ↓
Spatial Analysis (LEFT / CENTER / RIGHT)
      ↓
Proximity Estimation (FAR, CLOSE, VERY CLOSE)
      ↓
Navigation Decision Engine
      ↓
Virtual Motor Controller
      ↓
Live Dashboard
```

## Installation

Run the following commands in your terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

To start the dashboard:

```bash
source venv/bin/activate
streamlit run app.py
```

## Camera permissions

When you run the application for the first time, macOS may ask for camera permissions for your terminal (e.g., Terminal, iTerm2, or VS Code). You must allow this to access the built-in webcam.

If it fails, go to:
`System Settings` > `Privacy & Security` > `Camera`
and ensure your terminal application is toggled ON.

## Limitations

- **No True Distance Measurement:** YOLO does not directly measure distance. 
- **Monocular Estimation:** Current proximity estimation is monocular and approximate, based solely on bounding box size relative to the frame.
- **Virtual Motors:** The current motor controller is virtual and only outputs commands to the dashboard.
- **No Raspberry Pi Hardware:** Raspberry Pi hardware is not connected in this proof-of-concept.
- **Not a Medical Device:** This is a research/college prototype and NOT a safety-certified mobility device.

## Future Hardware Transition

The system is designed modularly. Moving to a hardware prototype will involve:

```text
MacBook Camera
      ↓
Raspberry Pi Camera

Virtual Motor
      ↓
Raspberry Pi GPIO
      ↓
Motor Driver
      ↓
Physical Motors
```

A Time-of-Flight (ToF) or ultrasonic sensor can later provide an independent distance/safety layer to complement the monocular YOLO proximity estimation.
