import tkinter as tk
from tkinter import filedialog, scrolledtext
from program import Program
from agent import Agent

class GUI:
    def __init__(self, master, program):
        self.master = master
        self.master.title("Wumpus World")
        self.cell_size = 90
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




    def run(self):
        self.master.mainloop()

    # def perform_action(self):
    #     action = self.action_entry.get()
    #     self.chat_output.insert(tk.END, f"Action: {action}\n")
    #     result = self.program.action(action)
    #     if result is not None:
    #         if isinstance(result, dict):
    #             self.show_knowledge_base(result)
    #         else:
    #             self.chat_output.insert(tk.END, f"Result: {result}\n")
    #     else:
    #         self.chat_output.insert(tk.END, "Invalid action\n")
    #     self.chat_output.insert(tk.END, "\n")
    #     self.chat_output.see(tk.END)
    #     self.action_entry.delete(0, tk.END)
    #     self.reload_map()

    def show_knowledge_base(self, kb):
        kb_text = "Knowledge Base:\n"
        for pos, content in kb.items():
            kb_text += f"Position {pos}: {content}\n"
        self.chat_output.insert(tk.END, kb_text + "\n")

    def show_message(self, message):
        self.chat_output.insert(tk.END, f"Message: {message}\n\n")
        self.chat_output.see(tk.END)