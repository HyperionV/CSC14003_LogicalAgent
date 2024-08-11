import tkinter as tk
from tkinter import filedialog
from program import Program
from agent import Agent

class GUI:
    def __init__(self, master, program):
        self.master = master
        self.master.title("Wumpus World")
        self.cell_size = 75
        self.grid_size = 10
        
        self.canvas = tk.Canvas(self.master, width=self.cell_size*self.grid_size, height=self.cell_size*self.grid_size)
        self.canvas.pack()
        
         # Create a frame for buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(fill=tk.X)

        # Create buttons side by side
        self.load_button = tk.Button(self.button_frame, text="Load Map", command=self.load_map)
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.action_button = tk.Button(self.button_frame, text="Perform Action", command=self.show_action_dialog)
        self.action_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.map_data = []
        self.program = program
        self.load_map()

        # Erase this to manually load the map
        program.set_gui(self)

    def load_map(self):
        # file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        file_path = "test.txt"
        if file_path:
            self.program.load_map(file_path)
            self.map_data = self.program.map
            self.draw_grid()

    def reload_map(self):
        print(self.program.agent)
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

                adjacent = [i - self.program.agent[0], j - self.program.agent[1]] in [[0, 1], [1, 0], [0, -1], [-1, 0]]

                if i < len(self.map_data) and j < len(self.map_data[i]):
                    cell_content = self.map_data[i][j]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white" if not adjacent else "light yellow", outline="black")
                    self.draw_cell_content(x1, y1, x2, y2, cell_content)

    def draw_cell_content(self, x1, y1, x2, y2, content, adjacents=False):
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

    def run(self):
        self.master.mainloop()
        self.show_action_dialog()

    def show_action_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Perform Action")

        action_label = tk.Label(dialog, text="Enter action:")
        action_label.pack()

        action_entry = tk.Entry(dialog)
        action_entry.pack()

        def perform_action():
            action = action_entry.get()
            result = self.program.action(action)
            if result is not None:
                if isinstance(result, dict):
                    self.show_knowledge_base(result)
                else:
                    self.show_message("Invalid action")
            dialog.destroy()

        perform_button = tk.Button(dialog, text="Perform", command=perform_action)
        perform_button.pack()

    def show_knowledge_base(self, kb):
        kb_dialog = tk.Toplevel(self.master)
        kb_dialog.title("Knowledge Base")
        for pos, content in kb.items():
            label = tk.Label(kb_dialog, text=f"Position {pos}: {content}")
            label.pack()

    def show_message(self, message):
        message_dialog = tk.Toplevel(self.master)
        message_dialog.title("Message")
        label = tk.Label(message_dialog, text=message)
        label.pack()