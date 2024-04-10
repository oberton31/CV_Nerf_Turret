import time
class PID:

    def __init__(self, kP = 1, kD = 0, kI = 0):
        # initialze gains
        self.kP = kP
        self.kD = kD
        self.kI = kI

        self.initialize()
        

    def initialize(self):
        # initialize delta t variables
        self.curr_tm = time.time()
        self.prev_tm = self.curr_tm

        self.prev_err = 0

        # term result variables
        self.cP = 0
        self.cI = 0
        self.cD = 0
        
    def update(self, error, sleep=0.2):
        # pause for a bit
        time.sleep(sleep)
        # grab the current time and calculate delta time
        self.curr_tm = time.time()
        deltaTime = self.curr_tm - self.prev_tm
        # delta error
        deltaError = error - self.prev_err
        # proportional term
        self.cP = error
        # integral term
        self.cI += error * deltaTime
        # derivative term and prevent divide by zero
        self.cD = (deltaError / deltaTime) if deltaTime > 0 else 0
        # save previous time and error for the next update
        self.prev_tm = self.curr_tm
        self.prev_err = error
        # sum the terms and return
        return sum([
            self.kP * self.cP,
            self.kI * self.cI,
            self.kD * self.cD])