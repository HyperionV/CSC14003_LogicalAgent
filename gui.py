import tkinter as tk
from tkinter import filedialog, scrolledtext
from program import Program
from agent import Agent

class GUI:
    def __init__(self, master, program):
        self.master = master
        self.master.title("Wumpus World")
        self.cell_size = 75
        self.grid_size = 10
        
        # Main frame to hold everything
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for map and buttons
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.left_frame, width=self.cell_size*self.grid_size, height=self.cell_size*self.grid_size)
        self.canvas.pack(pady=10)
        
        # Create a frame for buttons
        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.load_button = tk.Button(self.button_frame, text="Load Map", command=self.load_map, height=2)
        self.load_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # self.action_button = tk.Button(self.button_frame, text="Perform Action", command=self.perform_action, height=2)
        # self.action_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_output = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=40, height=20)
        self.chat_output.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Frame for input field and send button
        self.input_frame = tk.Frame(self.right_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 5))

        # Larger input field
        self.action_entry = tk.Entry(self.input_frame, font=('Arial', 12))
        self.action_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.send_button = tk.Button(self.right_frame, text="Send", command=self.perform_action, height=2)
        self.send_button.pack(fill=tk.X)

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

    def perform_action(self):
        action = self.action_entry.get()
        self.chat_output.insert(tk.END, f"Action: {action}\n")
        result = self.program.action(action)
        if result is not None:
            if isinstance(result, dict):
                self.show_knowledge_base(result)
            else:
                self.chat_output.insert(tk.END, f"Result: {result}\n")
        else:
            self.chat_output.insert(tk.END, "Invalid action\n")
        self.chat_output.insert(tk.END, "\n")
        self.chat_output.see(tk.END)
        self.action_entry.delete(0, tk.END)
        self.reload_map()

    def show_knowledge_base(self, kb):
        kb_text = "Knowledge Base:\n"
        for pos, content in kb.items():
            kb_text += f"Position {pos}: {content}\n"
        self.chat_output.insert(tk.END, kb_text + "\n")

    def show_message(self, message):
        self.chat_output.insert(tk.END, f"Message: {message}\n\n")
        self.chat_output.see(tk.END)