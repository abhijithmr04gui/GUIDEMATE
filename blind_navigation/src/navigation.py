from typing import List, Dict, Any
from src.config import TEMPORAL_SMOOTHING_FRAMES

class NavigationEngine:
    def __init__(self):
        self.command_history = []
        self.last_stable_command = "FORWARD"

    def decide(self, enriched_detections: List[Dict[str, Any]]) -> str:
        """
        Decides the next movement based on enriched detections.
        Each item in enriched_detections should have:
        'zone', 'proximity'
        """
        
        # Determine blocked zones (only CLOSE or VERY CLOSE obstacles matter)
        left_blocked = False
        center_blocked = False
        right_blocked = False
        very_close_center = False
        
        for d in enriched_detections:
            zone = d['zone']
            prox = d['proximity']
            
            # Immediate danger
            if zone == "CENTER" and prox == "VERY CLOSE":
                very_close_center = True
                
            if prox in ["CLOSE", "VERY CLOSE"]:
                if zone == "LEFT":
                    left_blocked = True
                elif zone == "CENTER":
                    center_blocked = True
                elif zone == "RIGHT":
                    right_blocked = True
        
        # Raw decision for current frame
        raw_decision = "FORWARD"
        
        # Rule 1: Immediate danger
        if very_close_center:
            raw_decision = "STOP"
        # Rule 5: All blocked
        elif left_blocked and center_blocked and right_blocked:
            raw_decision = "STOP"
        # Rule 2: Center blocked
        elif center_blocked:
            if not left_blocked:
                raw_decision = "MOVE LEFT"
            elif not right_blocked:
                raw_decision = "MOVE RIGHT"
            else:
                raw_decision = "STOP"
        # Rule 3: Left blocked
        elif left_blocked and not right_blocked:
            raw_decision = "MOVE RIGHT"
        # Rule 4: Right blocked
        elif right_blocked and not left_blocked:
            raw_decision = "MOVE LEFT"

        # Temporal Smoothing
        # STOP is highly prioritized and skips smoothing for safety
        if raw_decision == "STOP":
            self.last_stable_command = "STOP"
            self.command_history.clear()
            return "STOP"
            
        self.command_history.append(raw_decision)
        if len(self.command_history) > TEMPORAL_SMOOTHING_FRAMES:
            self.command_history.pop(0)
            
        # Change command only if the new command is consistent for N frames
        if len(self.command_history) == TEMPORAL_SMOOTHING_FRAMES and all(c == raw_decision for c in self.command_history):
            self.last_stable_command = raw_decision
            
        return self.last_stable_command
