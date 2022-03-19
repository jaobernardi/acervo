import logging
import time

enabled = False

class Timer:
    def __init__(self, function):
        if not enabled:
            return function

        self.function = function
    
    def __call__(self, *args, **kwds):
        logging.info(f"Executing function{self.function.__qualname__} with arguments: {args} and {kwds}")
        pre_call = time.time()
        response = self.function(*args, **kwds)
        post_call = time.time()
        total_time = post_call-pre_call
        ms = round(total_time*1000)
        logging.info(f"Function {self.function.__qualname__} took {ms}ms")
        return response