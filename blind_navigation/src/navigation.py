from typing import List, Dict, Any

class NavigationEngine:
    def __init__(self):
        pass

    def decide(self, enriched_detections: List[Dict[str, Any]]) -> str:
        """
        Decides the next movement based on enriched detections.
        Each item in enriched_detections should have:
        'zone', 'proximity'
        """
        
        # Determine blocked zones
        left_blocked = False
        center_blocked = False
        right_blocked = False
        
        very_close_center = False
        
        for d in enriched_detections:
            zone = d['zone']
            prox = d['proximity']
            
            # Any obstacle considered blocking if it's CLOSE or VERY CLOSE?
            # The prompt says:
            # Rule 1 — Center obstacle very close -> STOP
            if zone == "CENTER" and prox == "VERY CLOSE":
                very_close_center = True
                
            if prox in ["CLOSE", "VERY CLOSE"]:
                if zone == "LEFT":
                    left_blocked = True
                elif zone == "CENTER":
                    center_blocked = True
                elif zone == "RIGHT":
                    right_blocked = True
        
        # Rule 1
        if very_close_center:
            return "STOP"
            
        # Rule 5
        if left_blocked and center_blocked and right_blocked:
            return "STOP"
            
        # Rule 2: Center obstacle
        if center_blocked:
            # check whether left/right is blocked
            if not left_blocked:
                return "MOVE LEFT" # choose clear side
            elif not right_blocked:
                return "MOVE RIGHT"
            else:
                return "STOP"
                
        # Rule 3: Left obstacle
        if left_blocked and not right_blocked:
            return "MOVE RIGHT"
            
        # Rule 4: Right obstacle
        if right_blocked and not left_blocked:
            return "MOVE LEFT"
            
        # Rule 6: No relevant obstacle
        return "FORWARD"
