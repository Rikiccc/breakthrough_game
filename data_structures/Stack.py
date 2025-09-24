class Stack(object):
    def __init__(self):
        self._data = []
    def __len__(self):
        return len(self._data)
    def is_empty(self):
        return len(self._data) == 0
    def push(self,v):
        self._data.append(v)
    def top(self):
        if len(self._data) == 0:
            raise Exception("Stek je prazan")
        return self._data[-1]
    def pop(self):
        if len(self._data) == 0:
            raise Exception("Stek je prazan")
        return self._data.pop()