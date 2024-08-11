import tkinter as tk
from tkinter import filedialog
from program import Program
from agent import Agent

class GUI:
    def __init__(self, master, program, agent):
        self.master = master
        self.master.title("Wumpus World")
        self.cell_size = 50
        self.grid_size = 10
        
        self.canvas = tk.Canvas(self.master, width=self.cell_size*self.grid_size, height=self.cell_size*self.grid_size)
        self.canvas.pack()
        
        self.load_button = tk.Button(self.master, text="Load Map", command=self.load_map)
        self.load_button.pack()
        
        self.map_data = []
        self.program = program
        self.agent = agent

    def load_map(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.program.load_map(file_path)
            self.map_data = self.program.map
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                
                if i < len(self.map_data) and j < len(self.map_data[i]):
                    cell_content = self.map_data[i][j]
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

if __name__ == "__main__":
    root = tk.Tk()
    program = Program()
    agent = Agent(program)
    app = GUI(root, program, agent)
    root.mainloop()