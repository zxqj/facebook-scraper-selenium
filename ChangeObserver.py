import time
from output import debug

class ChangeObserver(object):
    def __init__(self, delay, callback):
        self.delay = delay
        self.callback = callback
        self.newState = self.lastState = None

    def generate_next_state(self):
        pass

    def describe_change(self, x1, x2):
        pass

    def generate_and_time_next_state(self):
        start = time.time()
        res,finished = self.generate_next_state()
        debug("check completed ("+str(int(time.time() - start)) + "s)")
        return res,finished

    def run(self):
        while (True):
            if (self.lastState is None):
                res, finished = self.generate_and_time_next_state()
                self.newState = self.lastState = res
                time.sleep(self.delay)
                continue
            self.lastState = self.newState
            self.newState, finished = self.generate_and_time_next_state()
            if not (self.newState == self.lastState):
                self.callback(self.describe_change(self.lastState, self.newState))
            if finished:
                break
            time.sleep(self.delay)