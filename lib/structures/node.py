# Recursive dict node thing 
class NodeDict(object):
    def __init__(self, in_dict):
        self._original_dict = in_dict
        self.build()

    def build(self):
        self.dict = self._original_dict
        for k, v in self.dict.items():
            if isinstance(v, dict):
                self.dict[k] = NodeDict(v)

    def __setattr__(self, name, value):
        self._original_dict[name] = value
        self.build()
    
    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, key):
        return self.dict[key]

    def __repr__(self):
        return self._original_dict.__repr__()
    