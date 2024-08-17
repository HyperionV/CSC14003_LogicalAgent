from pathlib import Path
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk
from Utils import Action
import pyglet

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")
pyglet.options['win32_gdi_font'] = True
pyglet.font.add_file("fonts/Montserrat-Bold.ttf")


class Gui:
    # constructor
    def __init__(self, program):
        self.state = "pause"
        self.filename = "input.txt"
        self.program = program
        self.window = Tk()
        self.window.title("10CentWorld")
        self.window.geometry("1200x920")
        self.window.iconbitmap(self.relative_to_assets("icon2.ico"))
        self.window.configure(bg = "#171435")
        self.init()
        self.window.resizable(False, False)
    
    def clearMessage(self):
        self.messsageOutput.delete(1.0, END)
        
        
    def relative_to_assets(self, path: str) -> Path:
        return ASSETS_PATH / Path(path)

    def run(self):
        self.window.mainloop()
    
    def getCanvas(self):
        return self.canvas


    def showMessage(self, message):
        self.messsageOutput.insert(END,  message)
        self.messsageOutput.see(END)


    def handle_button_press(self, btn_name):
        if btn_name == "pauseresume":
            self.pauseresume_button_clicked()
        elif btn_name == "update":
            self.updateButtonClicked()
        elif btn_name == "reset":
            self.resetButtonClicked()
        elif btn_name == "forward":
            self.forwardButtonClicked()

    def pauseresume_button_clicked(self):
        if(self.program.isActionListEmpty()):
            return
        self.changePauseresumeState("resume")
        self.program.runAgent()
        # self.program.agentDoWithUi(Action.SHOOT)
        pass    

        
    def forwardButtonClicked(self):
        if(self.program.isActionListEmpty()):
            return
        self.program.stepRun()
        pass
        
    def resetButtonClicked(self):
        if(self.state == "resume"):
            return
        self.clearMessage()
        self.program.load(self.filename, self.isVisible.get())
            
            
    def updateButtonClicked(self):
        if(self.state == "resume"):
            return
        self.clearMessage()
        self.filename = self.getMazeOption()
        self.program.load(self.filename, self.isVisible.get())
        self.program.getActionList()
        
    
        
    def getMazeOption(self):
        maze = self.maze_option.get()
        path = {
            "Map 1": "input1.txt",
            "Map 2": "input2.txt",
            "Map 3": "input3.txt",
            "Map 4": "input4.txt",
            "Map 5": "input5.txt",
            "Read from file": "input.txt"
        }
        return path.get(maze) 
        
    # ~ FUNCTIONS FOR BUTTONS FOR CHANGING TABS ~
    def changePauseresumeState(self, state):
        if state == "pause":
            self.pauseresume_button.config(image=self.pause_image,text="Pause")
        elif state == "resume":
            self.pauseresume_button.config(image=self.resume_image,text="Resume")
        self.state = state
        


        
    def init(self):
        self.sidebar = Canvas(
            self.window,
            bg = '#171435',
            height = 950,
            width = 300,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas = Canvas(
            self.window,
            bg = '#171435',
            height = 900,
            width = 900,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.sidebar.place(x= 915, y= 0)
        self.canvas.place(x = 10, y = 15)


        self.sidebar.create_text(
            55.0,
            100.0,
            anchor="nw",
            text="Map",
            fill="#FFFFFF",
            font=("Montserrat-Bold", 12 * -1)
        )
        self.maze_option= ttk.Combobox(
            values=["Map 1", "Map 2", "Map 3", "Map 4", "Map 5", "Read from file"],
            state="readonly",
            justify="center",
            font=("Montserrat-Bold", 14 * -1)
        )
        self.maze_option.current(5)
        self.maze_option.place(
            x=970.0,
            y=125.0,
            width=182.0,
            height=34.0
        )

        self.isVisible = BooleanVar()

        # Create a Checkbutton widget
        self.checkbox = Checkbutton(self.sidebar, foreground= "black", variable=self.isVisible, command= None, background= '#171435', activebackground= "#171435")
        self.checkbox.place(
            x=170.0,
            y=97.0,
        )
        self.sidebar.create_text(
            197.0,
            103.0,
            anchor="nw",
            text="Visible",
            fill="#FFFFFF",
            font=("Montserrat-Bold", 12 * -1)
        )
        self.update_button = Button(
                    self.sidebar, 
                    background= '#C67FFC',
                    height= 1,
                    foreground= "#171435",
                    highlightthickness= 2,
                    highlightbackground= '#f5267b',
                    highlightcolor= "WHITE",
                    activebackground= "WHITE", 
                    activeforeground= 'BLACK',
                    border= 0,
                    text= 'Update',
                    font= ("Montserrat-Bold", 14 * -1),
                    command= lambda: self.handle_button_press("update")
                )

        self.update_button.place(
            x=55.0,
            y=180.0,
            width=182.0,
            height=34.0
        )

        ######## PREVIOUS-PAUSERESUME-FORWARD BUTTONS #######

        ######## (i) PAUSE-RESUME BUTTON #######
        self.pause_image = PhotoImage(
            file=self.relative_to_assets("button_4.png"))
        self.resume_image = PhotoImage(
            file=self.relative_to_assets("button_3.png"))

        self.pauseresume_button = Button(
            image=self.pause_image,
            borderwidth=0,
            bg="#171435",
            highlightthickness=0,
            command=lambda: self.handle_button_press("pauseresume"),
            relief="flat",
            text=str("Pause"),
            activebackground="#171435",
            activeforeground="#171435"
        )
        self.pauseresume_button.place(
            x=1040.0,
            y=250.0,
            width=40.18182373046875,
            height=40.436981201171875
        )
        ########################################

        ######## (ii)  FORWARD BUTTON ##########
        self.Forward_button_image = PhotoImage(
            file=self.relative_to_assets("button_5.png"))
        self.Forward_button = Button(
            image=self.Forward_button_image,
            borderwidth=0,
            bg="#171435",
            highlightthickness=0,
            command= lambda: self.handle_button_press("forward"),
            relief="flat"
        )
        self.Forward_button.place(
            x=1116.0,
            y=250.0,
            width=40.18182373046875,
            height=40.0
        )
        ########################################

        ###### (iii)  PREVIOUS BUTTON ##########
        self.Reset_button_image = PhotoImage(
            file=self.relative_to_assets("button_6.png"))
        self.Reset_button = Button(
            image=self.Reset_button_image,
            borderwidth=0,
            bg="#171435",
            highlightthickness=0,
            command= lambda: self.handle_button_press("reset"),
            relief="flat"
        )
        self.Reset_button.place(
            x=968.0,
            y=250.0,
            width=40.18182373046875,
            height=40.0
        )
        self.sidebar.create_text(
            10.0,
            335.0,
            anchor="nw",
            text="Information",
            fill="#FFFFFF",
            font=("Montserrat-Bold", 12 * -1)
        )
        self.messsageOutput = scrolledtext.ScrolledText(self.sidebar, wrap=WORD, width=30, height=25)
        self.messsageOutput.place(x=10, y=360)


        self.sidebar.create_text(             
            170,
            25.0,
            anchor="nw",
            text="World",
            fill="#FFFFFF",
            font=("Montserrat-Bold", 32 * -1)
        )
        self.sidebar.create_text(             
            57.0,
            25.0,
            anchor="nw",
            text="10Cent",
            fill="yellow",
            font=("Montserrat-Bold", 32 * -1)
        )
        self.sidebar.create_text(             
            220.0,
            895.0,
            anchor="nw",
            text="10Cent",
            fill="yellow",
            font=("Montserrat-Bold", 9)
        )