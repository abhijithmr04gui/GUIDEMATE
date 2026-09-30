import streamlit as st
import cv2
import sys
import os
import time

# Add the project root to the path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.camera import Camera
from src.detector import ObjectDetector
from src.distance import estimate_proximity, get_zone
from src.navigation import NavigationEngine
from src.motor import VirtualMotorController
from src.config import CAMERA_INDEX, CONFIDENCE_THRESHOLD

# Configure page (Dark theme defaults in Streamlit, but we can enforce some CSS if needed)
st.set_page_config(page_title="AI Vision Navigation Assistant", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for high contrast and clean design
st.markdown("""
<style>
    .big-font {
        font-size:2.5rem !important;
        font-weight: bold;
    }
    .decision-stop {
        color: #ff4b4b;
        font-size: 3rem !important;
        font-weight: 900;
        text-align: center;
        background-color: rgba(255, 75, 75, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff4b4b;
    }
    .decision-move {
        color: #00cc66;
        font-size: 3rem !important;
        font-weight: 900;
        text-align: center;
        background-color: rgba(0, 204, 102, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #00cc66;
    }
    .decision-forward {
        color: #3399ff;
        font-size: 3rem !important;
        font-weight: 900;
        text-align: center;
        background-color: rgba(51, 153, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #3399ff;
    }
    .pipeline {
        font-family: monospace;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 20px;
        color: #aaaaaa;
    }
    .pipeline-active {
        color: #ffffff;
        font-weight: bold;
        background-color: #333333;
        padding: 5px 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for models and controllers
if "detector" not in st.session_state:
    st.session_state.detector = ObjectDetector()
if "camera" not in st.session_state:
    st.session_state.camera = Camera(CAMERA_INDEX)
if "nav_engine" not in st.session_state:
    st.session_state.nav_engine = NavigationEngine()
if "motor" not in st.session_state:
    st.session_state.motor = VirtualMotorController()
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "last_spoken_decision" not in st.session_state:
    st.session_state.last_spoken_decision = None
if "last_spoken_time" not in st.session_state:
    st.session_state.last_spoken_time = 0
if "available_cameras" not in st.session_state:
    # Scan for available cameras only once on startup
    st.session_state.available_cameras = Camera.scan_cameras()

def start_camera():
    st.session_state.is_running = True

def stop_camera():
    st.session_state.is_running = False
    if st.session_state.camera.is_connected:
        st.session_state.camera.release()

# Sidebar Controls
st.sidebar.title("Controls")

st.sidebar.markdown("### Camera Source")

def refresh_cameras():
    st.session_state.available_cameras = Camera.scan_cameras()

st.sidebar.button("🔄 Refresh Camera List", on_click=refresh_cameras, use_container_width=True)

# Create human readable labels for cameras
cam_options = {}
for idx in st.session_state.available_cameras:
    if idx == 0:
        cam_options[idx] = f"{idx} - MacBook Camera"
    else:
        cam_options[idx] = f"{idx} - External / Camo Android Phone"
        
if len(cam_options) == 0:
    st.sidebar.error("No cameras detected!")
    selected_cam_index = 0
else:
    # Allow user to pick from scanned cameras, or try an arbitrary one
    selected_cam_label = st.sidebar.selectbox("Select Camera", list(cam_options.values()))
    # Reverse lookup the index
    selected_cam_index = [k for k, v in cam_options.items() if v == selected_cam_label][0]

st.sidebar.markdown("---")

st.sidebar.button("Start Camera", on_click=start_camera, use_container_width=True)
st.sidebar.button("Stop Camera", on_click=stop_camera, use_container_width=True)

st.sidebar.markdown("---")
enable_detection = st.sidebar.checkbox("Start Detection", True)
enable_audio = st.sidebar.checkbox("Enable Audio Guidance", True)
simulation_mode = st.sidebar.checkbox("Demo Mode (Simulated)", False)

st.sidebar.markdown("---")
conf_thresh = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, CONFIDENCE_THRESHOLD, 0.05)
model_selection = st.sidebar.selectbox("YOLO Model", ["yolo11n.pt"])

# Header
st.title("AI Vision Navigation Assistant")
st.markdown("### Real-Time Obstacle Detection & Navigation for Visually Impaired Users")

camera_status_placeholder = st.empty()

# Layout: Left side for Video (dominant), Right side for Status & Controls
col_vid, col_stat = st.columns([2.5, 1.2])

with col_vid:
    pipeline_placeholder = st.empty()
    video_placeholder = st.empty()

with col_stat:
    decision_placeholder = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Navigation Status")
    nav_status_placeholder = st.empty()
    
    st.markdown("### System Status")
    system_status_placeholder = st.empty()

st.markdown("### Detection Information")
debug_placeholder = st.empty()

def get_simulated_detections(elapsed_time, width, height):
    scenario = int((elapsed_time // 5) % 5)
    from src.detector import Detection
    
    if scenario == 0:
        return []
    elif scenario == 1:
        return [Detection(object_name="person", confidence=0.99, x1=10, y1=100, x2=width//4, y2=height-100, center_x=width//8, center_y=height//2, width=width//4-10, height=height-200)]
    elif scenario == 2:
        return [Detection(object_name="person", confidence=0.99, x1=width - width//4, y1=100, x2=width-10, y2=height-100, center_x=width - width//8, center_y=height//2, width=width//4-10, height=height-200)]
    elif scenario == 3:
        return [Detection(object_name="person", confidence=0.99, x1=width//4, y1=10, x2=3*width//4, y2=height-10, center_x=width//2, center_y=height//2, width=width//2, height=height-20)]
    elif scenario == 4:
        return [
            Detection(object_name="person", confidence=0.99, x1=10, y1=100, x2=width//4, y2=height-100, center_x=width//8, center_y=height//2, width=width//4, height=height-200),
            Detection(object_name="car", confidence=0.99, x1=width//4 + 10, y1=100, x2=3*width//4 - 10, y2=height-100, center_x=width//2, center_y=height//2, width=width//2-20, height=height-200),
            Detection(object_name="bench", confidence=0.99, x1=3*width//4, y1=100, x2=width-10, y2=height-100, center_x=7*width//8, center_y=height//2, width=width//4-10, height=height-200)
        ]
    return []

def draw_visuals(frame, detections, enriched_data, width, height, decision):
    # Draw zone boundaries cleanly
    overlay = frame.copy()
    cv2.line(overlay, (width // 3, 0), (width // 3, height), (255, 255, 255), 1)
    cv2.line(overlay, (2 * width // 3, 0), (2 * width // 3, height), (255, 255, 255), 1)
    cv2.putText(overlay, "LEFT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(overlay, "CENTER", (width // 3 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(overlay, "RIGHT", (2 * width // 3 + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    for i, d in enumerate(detections):
        x1, y1, x2, y2 = d.x1, d.y1, d.x2, d.y2
        
        info = enriched_data[i]
        color = (0, 0, 255) if info['proximity'] == "VERY CLOSE" else (0, 255, 255) if info['proximity'] == "CLOSE" else (0, 255, 0)
        
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 3)
        
        label = f"{d.object_name.upper()} {d.confidence:.2f}"
        zone_label = info['zone']
        prox_label = info['proximity']
        
        # Background for text
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(overlay, (x1, y1 - 30), (x1 + text_size[0], y1), color, -1)
        cv2.putText(overlay, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.putText(overlay, f"{zone_label} | {prox_label}", (x1, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return overlay

def render_pipeline(decision_made=False, audio_played=False):
    html = '<div class="pipeline">'
    html += '<span class="pipeline-active">CAMERA</span> &rarr; '
    html += '<span class="pipeline-active">YOLO</span> &rarr; '
    
    if decision_made:
        html += '<span class="pipeline-active">NAVIGATION</span> &rarr; '
    else:
        html += 'NAVIGATION &rarr; '
        
    if audio_played:
        html += '<span class="pipeline-active">AUDIO</span>'
    else:
        html += 'AUDIO'
    html += '</div>'
    return html

if st.session_state.is_running:
    # Reconnect if camera is not connected or if the user selected a different camera
    if not st.session_state.camera.is_connected or st.session_state.camera.camera_index != selected_cam_index:
        if st.session_state.camera.is_connected:
            st.session_state.camera.release()
        st.session_state.camera.connect(selected_cam_index)
        
    if not st.session_state.camera.is_connected:
        if selected_cam_index != 0:
            camera_status_placeholder.error("""
            🔴 **Camo Camera not available.**
            
            Please:
            1. Open Camo Studio on the MacBook.
            2. Connect your Android phone.
            3. Confirm that the phone preview is visible.
            4. Restart the application if necessary.
            """)
        else:
            camera_status_placeholder.error("Status: 🔴 CAMERA NOT AVAILABLE")
            
        st.session_state.is_running = False
    else:
        camera_status_placeholder.success(f"Status: 🟢 CAMERA {selected_cam_index} CONNECTED & ACTIVE")
        frame_count = 0
        start_time = time.time()
        
        while st.session_state.is_running:
            frame_start = time.time()
            
            frame = st.session_state.camera.get_frame()
            if frame is None:
                video_placeholder.error("Failed to read frame")
                break
                
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            height, width, _ = frame.shape
            
            # Detect
            detections = []
            if simulation_mode:
                detections = get_simulated_detections(elapsed, width, height)
            elif enable_detection:
                detections = st.session_state.detector.detect(frame, conf_thresh)
                
            enriched_data = []
            for d in detections:
                zone = get_zone(d.center_x, width)
                prox = estimate_proximity(d, height)
                enriched_data.append({"zone": zone, "proximity": prox})
                
            # Navigate
            decision = st.session_state.nav_engine.decide(enriched_data)
            motor_state = st.session_state.motor.execute(decision)
            
            # Audio Feedback
            current_time = time.time()
            audio_played = False
            if enable_audio:
                if decision != st.session_state.last_spoken_decision or (current_time - st.session_state.last_spoken_time > 3.0):
                    if decision in ["MOVE LEFT", "MOVE RIGHT", "STOP"]:
                        os.system(f"say '{decision}' &")
                        audio_played = True
                    st.session_state.last_spoken_decision = decision
                    st.session_state.last_spoken_time = current_time
            
            # Draw on frame
            frame = draw_visuals(frame, detections, enriched_data, width, height, decision)
            
            # Convert BGR to RGB for Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Latency calculation
            latency_ms = (time.time() - frame_start) * 1000
            
            # Rendering updates
            pipeline_placeholder.markdown(render_pipeline(decision_made=True, audio_played=audio_played), unsafe_allow_html=True)
            video_placeholder.image(frame_rgb, channels="RGB", width="stretch")
            
            # Format prominent decision UI
            if decision == "STOP":
                decision_cls = "decision-stop"
            elif "MOVE" in decision:
                decision_cls = "decision-move"
            else:
                decision_cls = "decision-forward"
                
            decision_html = f"<div class='{decision_cls}'>{decision}</div>"
            decision_placeholder.markdown(decision_html, unsafe_allow_html=True)
            
            # Navigation Status Panel
            primary_obstacle = "None"
            primary_zone = "N/A"
            primary_prox = "N/A"
            if len(detections) > 0:
                # Find most critical obstacle (highest proxy, closest to center)
                primary_obstacle = detections[0].object_name.capitalize()
                primary_zone = enriched_data[0]['zone']
                primary_prox = enriched_data[0]['proximity']
            
            nav_status_md = f"""
| Metric | Value |
|---|---|
| **Command** | `{decision}` |
| **Obstacle** | {primary_obstacle} |
| **Position** | {primary_zone} |
| **Proximity** | {primary_prox} |
| **Total Objects** | {len(detections)} |
"""
            nav_status_placeholder.markdown(nav_status_md)
            
            # System Status Panel
            audio_status = "🟢 Active" if enable_audio else "🔴 Inactive"
            yolo_status = "🟢 Running" if enable_detection else "🔴 Stopped"
            if simulation_mode:
                yolo_status = "🟣 Simulated"
                
            system_status_md = f"""
- **Camera:** 🟢 Connected
- **YOLO:** {yolo_status}
- **Audio:** {audio_status}
- **FPS:** `{fps:.1f}`
- **Latency:** `{latency_ms:.1f} ms`
"""
            system_status_placeholder.markdown(system_status_md)
            
            # Detection info expander
            with debug_placeholder.container():
                with st.expander("Technical Details", expanded=False):
                    if len(detections) > 0:
                        det_table = "| Class | Confidence | Zone | Proximity | Bounding Box |\n|---|---|---|---|---|\n"
                        for d, info in zip(detections, enriched_data):
                            det_table += f"| {d.object_name} | {d.confidence:.2f} | {info['zone']} | {info['proximity']} | ({d.x1},{d.y1}) to ({d.x2},{d.y2}) |\n"
                        st.markdown(det_table)
                    else:
                        st.info("No objects detected in current frame.")
                        
                    st.write(f"**Inference Latency:** {latency_ms:.1f} ms")
                    st.write(f"**Application FPS:** {fps:.2f}")

            time.sleep(0.03) # small sleep to prevent 100% CPU

else:
    if st.session_state.camera.is_connected:
        st.session_state.camera.release()
    camera_status_placeholder.info("Status: ⚪ CAMERA INACTIVE - Click 'Start Camera' in the sidebar.")
    pipeline_placeholder.markdown(render_pipeline(), unsafe_allow_html=True)
    video_placeholder.info("Waiting for camera feed...")
    
    decision_placeholder.empty()
    nav_status_placeholder.empty()
    system_status_placeholder.empty()
    debug_placeholder.empty()
