from Utils import *
from Cell import Cell
from Agent import AgentProperties
from Gui import Gui
import tkinter as tk

class Program:
    def __init__(self, width, height, filename):
        self.objectImage = {}
        self.cellSize = 90
        self.width = width
        self.height = height
        self.Gui = Gui(self)
        self.canvas = self.Gui.getCanvas()
        self.loadObjectsImage()
        self.init(filename)
    
    def run(self):
        self.Gui.run()
        
    
    def init(self, filename):
        self.map = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.agentInfo = AgentProperties()
        self.readMap(filename)
        self.updatePercept()
        self.drawMap()

    def loadObjectsImage(self):
        self.objectImage[Environment.WUMPUS] = tk.PhotoImage(file=ASSET_PATH + "wumpus.png")
        self.objectImage[Environment.PIT] = tk.PhotoImage(file=ASSET_PATH + "pit.png")
        
        self.objectImage[Environment.POISON] = tk.PhotoImage(file=ASSET_PATH + "poision.png")
        self.objectImage[ItemType.HEAL] = tk.PhotoImage(file=ASSET_PATH + "health.png")
        self.objectImage[ItemType.GOLD] = tk.PhotoImage(file=ASSET_PATH + "gold.png")
        self.objectImage[ItemType.ARROW] = []
        self.objectImage[Environment.AGENT] = []
        for i in range (4):
            self.objectImage[ItemType.ARROW].append(tk.PhotoImage(file=ASSET_PATH + "arrow" + str(i) + ".png"))
        for i in range (4):
            self.objectImage[Environment.AGENT].append(tk.PhotoImage(file=ASSET_PATH + "agent" + str(i) + ".png"))
    def convertMatrixToMap(self, matrix):
        for i in range(self.height):
            for j in range(self.width):
                cell = matrix[i][j]
                cell_objects = getObjectsEnumArray(cell)
                self.map[i][j].addObjects(cell_objects)

    def readMap(self, filename):
        with open(filename, 'r') as f:
            matrix = []
            for line in f:
                matrix.append(line.strip().split('.'))
        self.convertMatrixToMap(matrix)

    def getMap(self):
        return self.map
    
    def updatePercept(self):
        # Update percept for each cell according to the objects in the adjacent cells
        for i in range(self.height):
            for j in range(self.width):
                percept = Percept(0)
                for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i + x >= 0 and i + x < self.height and j + y >= 0 and j + y < self.width:
                        obj = self.map[i + x][j + y].getObjects()
                        if obj[Environment.WUMPUS] > 0:
                            percept |= Percept.STENCH
                        if obj[Environment.PIT] > 0:
                            percept |= Percept.BREEZE
                        if obj[Environment.POISON] > 0:
                            percept |= Percept.WHIFF
                        if obj[Environment.HEAL] > 0:
                            percept |= Percept.GLOW
                self.map[i][j].updatePercept(percept)
                
    def agentDo(self, action):
        if action == Action.FORWARD:
            x, y = self.agentInfo.getPosition()
            if self.agentInfo.getDirection() == Direction.UP:
                x -= 1
            elif self.agentInfo.getDirection() == Direction.DOWN:
                x += 1
            elif self.agentInfo.getDirection() == Direction.LEFT:
                y -= 1
            elif self.agentInfo.getDirection() == Direction.RIGHT:
                y += 1
            if x >= 0 and x < self.height and y >= 0 and y < self.width:
                self.agentInfo.setPosition((x, y))
                self.showMessageOnGui(action)
                return True, self.agentInfo
            return False, self.agentInfo
            
        elif action == Action.TURN_RIGHT:
            direction = turnRight(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            self.showMessageOnGui(action)
            return True, self.agentInfo
        
        elif action == Action.TURN_LEFT:
            direction = turnLeft(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            self.showMessageOnGui(action)
            return True, self.agentInfo
        
        elif action == Action.GRAB:
            x, y = self.agentInfo.getPosition()
            if self.map[x][y].hasObject(Environment.GOLD):
                self.map[x][y].removeObject(Environment.GOLD)
                self.agentInfo.adjustInventory(ItemType.GOLD, 1)
                return True, self.agentInfo
            elif self.map[x][y].hasObject(Environment.HEAL):
                self.map[x][y].removeObject(Environment.HEAL)
                self.agentInfo.adjustInventory(ItemType.HEAL, 1)
                self.showMessageOnGui(action)
                return True, self.agentInfo
            else:
                return False, self.agentInfo
            
        elif action == Action.SHOOT:
            x, y = self.agentInfo.getPosition()
            nextX, nextY = x, y
            if self.agentInfo.getDirection() == Direction.UP:
                nextX -= 1
            elif self.agentInfo.getDirection() == Direction.DOWN:
                nextX += 1
            elif self.agentInfo.getDirection() == Direction.LEFT:
                nextY -= 1
            elif self.agentInfo.getDirection() == Direction.RIGHT:
                nextY += 1
            if nextX >= 0 and nextX < self.height and nextY >= 0 and nextY < self.width:
                if self.map[nextX][nextY].hasObject(Environment.WUMPUS):
                    self.map[nextX][nextY].removeObject(Environment.WUMPUS)
                    self.animateShoot(nextX, nextY)
                    self.showMessageOnGui(action)
                    return True, self.agentInfo
            return False, self.agentInfo

        elif action == Action.CLIMB:
            x, y = self.agentInfo.getPosition()
            if x == 0 and y == 0:
                self.showMessageOnGui(action)
                return True, self.agentInfo
            return False, self.agentInfo
        
        elif action == Action.HEAL:
            if self.agentInfo.inventory[ItemType.HEAL] > 0:
                health = self.agentInfo.getHealth()
                health = min(health + 50, 100)
                self.agentInfo.setHealth(health)
                self.agentInfo.adjustInventory(ItemType.HEAL, -1)
                self.showMessageOnGui(action)
                return True, self.agentInfo
            return False, self.agentInfo
        
    

    # MAP ON GUI
    def drawMap(self):
        self.canvas.delete("all")
        for i in range(self.height):
            for j in range(self.width):
                x1 = j * self.cellSize
                y1 = i * self.cellSize
                x2 = x1 + self.cellSize
                y2 = y1 + self.cellSize
                agentPos = self.agentInfo.getPosition()
                adjacent = [i - agentPos[0], j - agentPos[1]] in [[0, 1], [1, 0], [0, -1], [-1, 0]]

                if i < self.height and j < self.width:
                    cellContent = self.map[i][j].getObjects()
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white" if not adjacent else "light yellow", outline="black")
                    self.drawCellContent(x1, y1, cellContent)
        self.drawAgent()      
        

    def drawAgent(self):
        x, y = self.agentInfo.getPosition()
        print(x, y)
        direction = self.agentInfo.getDirection()
        x1 = y * self.cellSize
        y1 = x * self.cellSize
        self.canvas.create_image(x1 + 49 ,y1 + 48, image=self.objectImage[Environment.AGENT][direction.value])

    def drawCellContent(self, x1, y1, content):
        if content[Environment.WUMPUS] > 0:
            self.canvas.create_image(x1 + 16, y1 + 18, image=self.objectImage[Environment.WUMPUS])
        if content[Environment.PIT] > 0:
            self.canvas.create_image(x1 + 45 , y1 + 44, image=self.objectImage[Environment.PIT])
        if content[Environment.POISON] > 0:
            self.canvas.create_image(x1 + 16, y1 + 78, image=self.objectImage[Environment.POISON])
        if content[Environment.GOLD] > 0:
            self.canvas.create_image(x1 + 76, y1 + 14, image=self.objectImage[ItemType.GOLD])
        if content[Environment.HEAL] > 0:
            self.canvas.create_image(x1 + 76, y1 + 76, image=self.objectImage[ItemType.HEAL])
        return

    def convertMapPosition(self, x, y):
        mapPos = self.height - x,  y + 1
        return mapPos         # (1, 1) (1, 2) ... (10, 10) (BL -> TR)

    def showMessageOnGui(self, action):
        agentPos = self.agentInfo.getPosition()
        message = ""
        message += "Action: "
        if action == Action.FORWARD:
            message += "Move forward"
        elif action == Action.TURN_RIGHT:
            message += "Turn right"
        elif action == Action.TURN_LEFT:
            message += "Turn left"
        elif action == Action.GRAB:
            message += "Grab"
        elif action == Action.SHOOT:
            message += "Shoot"
        elif action == Action.CLIMB:
            message += "Climb"
        elif action == Action.HEAL:
            message += "Heal"
        message += "\n"
        message += "Position: "
        message +=  str(self.convertMapPosition(agentPos[0], agentPos[1]))
        message += '\n'
        message += "Pecrepts: "
        percept = self.map[agentPos[0]][agentPos[1]].getPercept()
        if percept & Percept.STENCH:
            message += "Stench, "
        if percept & Percept.BREEZE:
            message += "Breeze, "
        if percept & Percept.SCREAM:
            message += "Scream, "
        if percept & Percept.WHIFF:
            message += "Whiff, "
        if percept & Percept.GLOW:
            message += "Glow, "
        message += "\n\n"
        self.Gui.showMessage(message)


    def animateShoot(self, nextX, nextY):
        steps = 30 
        delay = 1000 // steps 

        xStart, yStart = self.agentInfo.getPosition()
        direction = self.agentInfo.getDirection()
        xstart = yStart * self.cellSize + 45
        ystart = xStart * self.cellSize + 45
        nexty = nextX * self.cellSize + 45
        nextx = nextY * self.cellSize + 45




        xDiff = ((nextx - xstart)  / steps)
        yDiff = ((nexty - ystart) / steps)

        arrowId = self.canvas.create_image(xstart, ystart, image=self.objectImage[ItemType.ARROW][direction.value])

        def moveArrow(step):
            if step <= steps:
                self.canvas.move(arrowId, xDiff, yDiff)
                self.canvas.after(delay, moveArrow, step + 1)
            else:
                self.canvas.delete(arrowId)

        moveArrow(0)
    

    def reloadMap(self):
        self.drawMap()