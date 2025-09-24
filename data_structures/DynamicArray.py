class DynamicArray(object):
    def __init__(self, n: int, init=None):
        self._data = [init for _ in range(n)]
        self.n = n
    def __getitem__(self, i): 
        return self._data[i]
    def __setitem__(self, i, v): 
        self._data[i] = v
    def __len__(self): 
        return self.n