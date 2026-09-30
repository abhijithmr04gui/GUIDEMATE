class MotorController:
    def forward(self):
        raise NotImplementedError

    def left(self):
        raise NotImplementedError

    def right(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

class VirtualMotorController(MotorController):
    def __init__(self):
        self.current_state = "STOP"
        
    def forward(self):
        self.current_state = "FORWARD"
        print("MOTOR → FORWARD")
        return self.current_state

    def left(self):
        self.current_state = "LEFT"
        print("MOTOR → LEFT")
        return self.current_state

    def right(self):
        self.current_state = "RIGHT"
        print("MOTOR → RIGHT")
        return self.current_state

    def stop(self):
        self.current_state = "STOP"
        print("MOTOR → STOP")
        return self.current_state
        
    def execute(self, command: str):
        if command == "FORWARD":
            return self.forward()
        elif command == "MOVE LEFT":
            return self.left()
        elif command == "MOVE RIGHT":
            return self.right()
        else:
            return self.stop()
