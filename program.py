from room import Room
class Program:
    def __init__(self, canvas):
        self.canvas = canvas
        self.matrix = None
        self.map = None
        # self.original_map = None
        self.agent = [0,0]
        self.score = 0
        self.health = 100
        self.direction = [(0, 1), (1, 0), (0, -1)]
        self.agent_direction = 0
    
    def getObjectsStrArray(self, cellStr):
        cell_objects = []
        cell = cellStr.copy()
        # Handle multiple Wumpus (W)
        count_wumpus = cell.count('W')
        if count_wumpus > 0:
            cell_objects.extend(['W'] * count_wumpus)
            cell = cell.replace('W', '')

        # Handle Poisonous Gas (P_G)
        if "P_G" in cell:
            cell_objects.append('P_G')
            cell = cell.replace('P_G', '')

        # Handle Healing Potions (H_P)
        if "H_P" in cell:
            cell_objects.append('H_P')
            cell = cell.replace('H_P', '')

        # Handle Pit (P)
        if "P" in cell:
            cell_objects.append('P')
            cell = cell.replace('P', '')

        # Handle Agent (A)
        if "A" in cell:
            cell_objects.append('A')
            cell = cell.replace('A', '')

        # Handle Gold (G)
        if "G" in cell:
            cell_objects.append('G')
            cell = cell.replace('G', '')
        
        return cell_objects

    def convertMatrixToMap(self):
        # initialize map with size = matrix and fill with None
        matrix = [[None for _ in range(len(self.matrix))] for _ in range(len(self.matrix[0]))]

        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                cell = self.matrix[i][j]
                cell_objects = self.getObjectsStrArray(cell)
                self.map[i][j] = Room((i, j), len(self.matrix), cell_objects)


    def load_map(self, filename):
        with open(filename, 'r') as f:
            self.matrix = []
            for line in f:
                self.matrix.append(line.strip().split('.'))
        # if self.original_map is None:
        #     self.original_map = [[i for i in j] for j in self.map]
        self.convertMatrixToMap()
    
    def reload_map(self):
        self.map_data = self.program.map
        self.draw_grid()


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
            return "Turned left"
        elif mv == 'R':
            self.agent_direction = (self.agent_direction + 1) % 4
            return "Turned right"
        elif mv == 'F':
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
            return "Grab smth"
        elif mv == 'S':
            self.score -= 100
            pos = [self.agent[0] + self.direction[self.agent_direction][0], self.agent[1] + self.direction[self.agent_direction][1]]
            
            return 'S' if self.map[pos[0][pos[1]]] == 'W' else "Shoot smth"
        elif mv == 'C':
            if self.agent != [0,0]:
                return None
            else:
                print('You win')
                return None
        elif mv == 'H':
            pass
        else:
            print('Invalid action')
            return None            
        
    def getRoomPercepts(self, x, y):
        adj_cell_list = []
        adj_cell_matrix_pos_list = [(x, y + 1),   # Right
                                    (x, y - 1),   # Left
                                    (x - 1, y),   # Up
                                    (x + 1, y)]   # Down

        for ajd_cell_matrix_pos in adj_cell_matrix_pos_list:
            if 0 <= ajd_cell_matrix_pos[0] < len(self.map) and 0 <= ajd_cell_matrix_pos[1] < len(self.map[0]):
                adj_cell_list.append(self.map[ajd_cell_matrix_pos[0]][ajd_cell_matrix_pos[1]])

        adj_cell_list = self.map[x][y].get_adj_cell_list()
        percept = [0, 0, 0, 0, 0] # [-G, -B, -S, -W_H, -G_L]
        for i in adj_cell_list:
            percept[0] = (adj_cell_list[i].isExistGold() == True)
            percept[1] = (adj_cell_list[i].isExistPit() == True)
            percept[2] = (adj_cell_list[i].isExistWumpus() == True)
            percept[3] = (adj_cell_list[i].isExistPoisionousGas() == True)
            percept[4] = (adj_cell_list[i].isExistHealthPotion() == True)

        return percept
    
    def doAgentAction(self, action):
        

        
    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                adjacent = [i - self.program.agent[0], j - self.program.agent[1]] in [[0, 1], [1, 0], [0, -1], [-1, 0]]

                if i < len(self.map_data) and j < len(self.map_data[i]):
                    cell_content = self.map[i][j].getObjects()
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white" if not adjacent else "light yellow", outline="black")
                    self.draw_cell_content(x1, y1, x2, y2, cell_content)


    def draw_cell_content(self, x1, y1, x2, y2, content):
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        if 'W' in content:
            self.canvas.create_text(center_x, center_y, text="W", font=("Arial", 12, "bold"), fill="red")
        if 'P' in content:
            self.canvas.create_text(center_x, center_y, text="P", font=("Arial", 12, "bold"), fill="black")
        if 'A' in content:
            self.canvas.create_text(center_x, center_y, text="A", font=("Arial", 12, "bold"), fill="blue")
        if 'G' in content:
            self.canvas.create_text(center_x, center_y, text="G", font=("Arial", 12, "bold"), fill="gold")
        if 'P_G' in content:
            self.canvas.create_text(center_x, center_y, text="P_G", font=("Arial", 10, "bold"), fill="purple")
        if 'H_P' in content:
            self.canvas.create_text(center_x, center_y, text="H_P", font=("Arial", 10, "bold"), fill="green")
        if 'S' in content:
            self.canvas.create_text(center_x-10, center_y+10, text="S", font=("Arial", 8), fill="brown")
        if 'B' in content:
            self.canvas.create_text(center_x+10, center_y+10, text="B", font=("Arial", 8), fill="cyan")
        if 'W_H' in content: 
            self.canvas.create_text(center_x-10, center_y-10, text="W", font=("Arial", 8), fill="gray")
        if 'G_L' in content:
            self.canvas.create_text(center_x+10, center_y-10, text="G_L", font=("Arial", 8), fill="yellow")