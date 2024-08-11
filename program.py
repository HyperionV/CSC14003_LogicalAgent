class Program:
    def __init__(self):
        self.map = None
        self.original_map = None
        self.agent = [0,0]
        self.score = 0
        self.health = 100
        self.direction = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.agent_direction = 0
        self.gui = None

    def load_map(self, filename):
        with open(filename, 'r') as f:
            self.map = []
            for i in f:
                self.map.append(i.split('.'))
        if self.original_map == None:
            self.original_map = [[i for i in j] for j in self.map]

    def set_gui(self, gui):
        self.gui = gui

    def get_cell(self, x, y):
        if self.map is not None and 0 <= x < self.map.shape[0] and 0 <= y < self.map.shape[1]:
            return self.map[x, y]
        else:
            return None
        
    def check_valid_cell(self, cell):
        return 0 <= cell[0] < 10 and 0 <= cell[1] < 10
    
    def action(self, mv):
        self.score -= 10
        if mv == 'L':
            self.agent_direction = (self.agent_direction + 3) % 4
            return None
        elif mv == 'R':
            self.agent_direction = (self.agent_direction + 1) % 4
            return None
        elif mv == 'F':
            print(self.original_map)
            self.map[self.agent[0]][self.agent[1]] = self.original_map[self.agent[0]][self.agent[1]] if self.agent != [0,0] else '.'
            self.agent = [self.agent[i] + self.direction[self.agent_direction][i] for i in range(2)]
            self.map[self.agent[0]][self.agent[1]] = 'A'

            if self.map[self.agent[0]][self.agent[1]] in ['P', 'W']:
                print('You Deer')
                return None
            elif self.map[self.agent[0]][self.agent[1]] == 'P_G':
                self.heath -= 25

            kb = {}
            for i in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                pos = [i[j] + self.agent[j] for j in range(2)]
                if self.check_valid_cell(pos):
                    kb.update({(pos[0], pos[1]): self.map[pos[0]][pos[1]]})
                else:
                    continue
            self.gui.reload_map()
            print(kb)
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