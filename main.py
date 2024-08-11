import tkinter as tk
from program import Program
from agent import Agent
from gui import GUI
if __name__ == "__main__":
    root = tk.Tk()
    program = Program()
    app = GUI(root, program)
    app.run()