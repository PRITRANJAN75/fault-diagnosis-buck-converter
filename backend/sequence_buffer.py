import numpy as np

class SequenceBuffer:
    def __init__(self, size=50):
        self.size=size; self.buffer=[]

    def add(self,data):
        self.buffer.append(data)
        if len(self.buffer)>self.size:
            self.buffer.pop(0)

    def get_sequence(self):
        if len(self.buffer)<self.size:
            return None
        return np.array(self.buffer)
