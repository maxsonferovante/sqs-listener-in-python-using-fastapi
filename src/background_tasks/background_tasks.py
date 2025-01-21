import threading
import time 


class BackgroudTask(threading.Thread):
    def __init__(self, name: str, func: callable, interval: int):
        super().__init__()
        self.name = self.__validate_name(name)
        self.interval = self.__validate_interval(interval)
        self.func = self.__validate_func(func)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        self.join()
    

    def __validate_name(self, name):
        if name is None:
            return "Background Task - " + str(time.time())  
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        return name
    def __validate_interval(self, interval):
        if interval < 0:
            raise ValueError("Interval must be greater than 0")
        if interval < 1:
            raise ValueError("Interval must be an integer")
        if interval > 60:
            raise ValueError("Interval must be less than 60")
        return interval
    
    def __validate_func(self, func):
        if not callable(func):
            raise ValueError("Func must be callable")
        return func
    
    def run(self, *args, **kwargs):
        print(f"Running task {self.name}")
        
        while True:
            print(f"Task {self.name} is running")
            self.func()
            time.sleep(self.interval)