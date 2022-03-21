import time

def calc_percentage(total, perc):
    return int((total/100)*perc)


class TimeoutList:
    def __init__(self, ttl):
        self._store = {}
        self.ttl = ttl
    
    def check(self):
        for item in list(self._store):
            if self._store[item]['expiry'] <= time.time():
                self._store.pop(item)

    def append(self, item):
        self.check()
        self._store[item] = {"expiry": time.time()+self.ttl}    

    def __contains__(self, item):
        self.check()
        return item in self._store

    def __repr__(self):
        self.check()
        return list(self._store).__repr__()

    def __iter__(self):
        self.check()
        return self._store.__iter__()

