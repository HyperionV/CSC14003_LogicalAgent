import numpy as np

class Program:
    def __init__(self):
        self.map = None
        self.agent = [0,0]
        self.score = 0
        self.health = 100
        self.direction = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.agent_direction = 0

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
    
    def action(self, mv):
        self.score -= 10
        if mv == 'L':
            self.agent_direction = (self.agent_direction + 3) % 4
            return None
        elif mv == 'R':
            self.agent_direction = (self.agent_direction + 1) % 4
            return None
        elif mv == 'F':
            self.agent = [self.agent[i] + self.direction[self.agent_direction][i] for i in range(2)]
            if self.map[self.agent[0]][self.agent[1]] in ['P', 'W']:
                print('You Deer')
                return None
            elif self.map[self.agent[0]][self.agent[1]] == 'P_G':
                self.heath -= 25
            kb = {}
            for i in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                pos = [i[j] + self.agent[j] for j in range(2)]
                try:
                    kb.update({pos: self.map[pos[0]][pos[1]]})
                except:
                    continue
            return kb
        elif mv == 'G':
            if self.map[self.agent[0]][self.agent[1]] == 'G':
                self.score += 5000
                self.map[self.agent[0]][self.agent[1]] = '.'
        elif mv == 'S':
            self.score -= 100
            pos = [self.agent[0] + self.direction[self.agent_direction][0], self.agent[1] + self.direction[self.agent_direction][1]]
            return 'S' if self.map[pos[0][pos[1]]] == 'W' else None
        elif mv == 'C':
            if self.agent != [0,0]:
                print('You are not at the starting point')
                return None
            else:
                print('You win')
                return None
        elif mv == 'H':
            pass
        else:
            print('Invalid action')
            return None            