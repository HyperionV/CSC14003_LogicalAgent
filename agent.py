class Agent:
    def __init__(self, program):
        self.program = program
        self.x = 0
        self.y = 0

    def get_percepts(self):
        percepts = {
            'breeze': False,
            'stench': False,
            'whiff': False,
            'glow': False
        }
        for dx, dy in [(-1, 0), (1, 0), (0, -1)]:
            cell = self.program.get_cell(self.x + dx, self.y + dy)
            if cell == 'P':
                percepts['breeze'] = True
            elif cell == 'W':
                percepts['stench'] = True
            elif cell == 'P_G':
                percepts['whiff'] = True
            elif cell == 'H_P':
                percepts['glow'] = True
        return percepts