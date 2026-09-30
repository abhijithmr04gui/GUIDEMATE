import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.navigation import NavigationEngine
from src.config import TEMPORAL_SMOOTHING_FRAMES

def run_decision(engine, data):
    decision = ""
    for _ in range(TEMPORAL_SMOOTHING_FRAMES):
        decision = engine.decide(data)
    return decision

def test_no_obstacles():
    engine = NavigationEngine()
    decision = run_decision(engine, [])
    assert decision == "FORWARD"

def test_left_obstacle():
    engine = NavigationEngine()
    data = [{"zone": "LEFT", "proximity": "CLOSE"}]
    assert run_decision(engine, data) == "MOVE RIGHT"

def test_right_obstacle():
    engine = NavigationEngine()
    data = [{"zone": "RIGHT", "proximity": "CLOSE"}]
    assert run_decision(engine, data) == "MOVE LEFT"

def test_center_very_close():
    engine = NavigationEngine()
    data = [{"zone": "CENTER", "proximity": "VERY CLOSE"}]
    # STOP overrides smoothing, so even one call should return STOP
    assert engine.decide(data) == "STOP"

def test_center_left_blocked():
    engine = NavigationEngine()
    data = [
        {"zone": "CENTER", "proximity": "CLOSE"},
        {"zone": "LEFT", "proximity": "CLOSE"}
    ]
    assert run_decision(engine, data) == "MOVE RIGHT"

def test_center_right_blocked():
    engine = NavigationEngine()
    data = [
        {"zone": "CENTER", "proximity": "CLOSE"},
        {"zone": "RIGHT", "proximity": "CLOSE"}
    ]
    assert run_decision(engine, data) == "MOVE LEFT"

def test_all_blocked():
    engine = NavigationEngine()
    data = [
        {"zone": "LEFT", "proximity": "CLOSE"},
        {"zone": "CENTER", "proximity": "CLOSE"},
        {"zone": "RIGHT", "proximity": "CLOSE"}
    ]
    # STOP overrides smoothing
    assert engine.decide(data) == "STOP"

def test_center_far_obstacle():
    engine = NavigationEngine()
    data = [{"zone": "CENTER", "proximity": "FAR"}]
    assert run_decision(engine, data) == "FORWARD"
