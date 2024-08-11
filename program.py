import numpy as np

class Program:
    def __init__(self):
        self.map = None

    def load_map(self, filename):
        with open(filename, 'r') as f:
            self.map = []
            for i in f:
                self.map.append(i.split('.'))

    def get_cell(self, x, y):
        if self.map is not None and 0 <= x < self.map.shape[0] and 0 <= y < self.map.shape[1]:
            return self.map[x, y]
        else:
            return None