class HashMap(object): 
    def __init__(self): 
        self.d={}
    def get(self,k): 
        return self.d.get(k)
    def set(self,k,v): 
        self.d[k]=v