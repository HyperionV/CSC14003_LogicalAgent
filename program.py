from Utils import *
from Cell import Cell
from agent import AgentProperties
from agent import Agent
from agent import KB
from gui import Gui
import tkinter as tk

class Program:
    def __init__(self, width, height, filename):
        self.explored = []
        self.isvisible = False
        self.actionList = None
        self.current_step = 0
        self.objectImage = {}
        self.filename = filename
        self.outputFile = ''
        self.cellSize = 90
        self.width = width
        self.height = height
        self.Gui = Gui(self)
        self.canvas = self.Gui.getCanvas()
        self.dict = {
            Environment.WUMPUS: Percept.STENCH,
            Environment.PIT: Percept.BREEZE,
            Environment.POISON: Percept.WHIFF,
            Environment.HEAL: Percept.GLOW
        }
        self.loadObjectsImage()
        self.load(filename, False)

    def autoRun(self, speed, actionList):
        if(self.current_step == len(actionList) or actionList is None):
            self.Gui.changePauseresumeState("pause")
            return
        self.agentDoWithUi(actionList[self.current_step][0], actionList[self.current_step][1])
        self.canvas.after(speed, self.autoRun, speed, actionList)
        fileName = self.filename.split('input')[-1]
        with open(f"output/output{fileName}", 'w') as f:
            for item in self.outputFile:
                f.write(item)
        f.close()
        self.outputFile = ''
    
    def stepRun(self):
        if(self.current_step == len(self.actionList) or self.actionList is None):
            return
        self.agentDoWithUi(self.actionList[self.current_step][0], self.actionList[self.current_step][1])

    def runAgent(self):
        self.autoRun(300, self.actionList)

    def getActionList(self):
        self.agent = Agent(self.width, self.height) 
        self.actionList = self.agent.agentClear(self)
        self.load(self.filename, self.isvisible)
          
    def run(self):
        self.Gui.run()
    
    def load(self, filename, isVisible):
        self.isvisible = isVisible
        self.agent = Agent(self.width, self.height)
        self.explored.clear()
        self.filename = filename
        self.map = [[Cell() for _ in range(self.width)] for _ in range(self.height)]
        self.agentInfo = AgentProperties()
        self.readMap(filename)
        self.updatePercept()
        self.drawMap()
        self.current_step = 0

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
                        for x in self.dict.keys():
                            if obj[x] > 0:
                                percept |= self.dict[x]
                self.map[i][j].updatePercept(percept)

    def updatePerceptInPos(self, i, j):
        percept = Percept(0)
        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if i + x >= 0 and i + x < self.height and j + y >= 0 and j + y < self.width:
                obj = self.map[i + x][j + y].getObjects()
                for x in self.dict.keys():
                    if obj[x] > 0:
                        percept |= self.dict[x]
        self.map[i][j].updatePercept(percept)
    
    def getCurrentStep(self):   
        return self.current_step

    def isActionListEmpty(self):
        return self.actionList is None
    
    def getPercept(self, i, j):
        return self.map[i][j].getPercept()
    
    def getObject(self, i, j):
        return self.map[i][j].getObjects()
        
    def agentDo(self, action):
        isSuccessful = False
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
                isSuccessful = True
            
        elif action == Action.TURN_RIGHT:
            direction = turnRight(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            isSuccessful = True
        
        elif action == Action.TURN_LEFT:
            direction = turnLeft(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            isSuccessful = True
        
        elif action == Action.GRAB:
            x, y = self.agentInfo.getPosition()
            if self.map[x][y].hasObject(Environment.GOLD):
                self.map[x][y].removeObject(Environment.GOLD)
                self.agentInfo.adjustInventory(ItemType.GOLD, 1)
                isSuccessful = True
            elif self.map[x][y].hasObject(Environment.HEAL):
                self.map[x][y].removeObject(Environment.HEAL)
                self.agentInfo.adjustInventory(ItemType.HEAL, 1)
                isSuccessful = True
            
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
                    isSuccessful = True

        elif action == Action.CLIMB:
            x, y = self.agentInfo.getPosition()
            if x == 0 and y == 0:
                isSuccessful = True
        
        elif action == Action.HEAL:
            if self.agentInfo.inventory[ItemType.HEAL] > 0:
                health = self.agentInfo.getHealth()
                health = min(health + 25, 100)
                self.agentInfo.setHealth(health)
                self.agentInfo.adjustInventory(ItemType.HEAL, -1)
                isSuccessful = True

        elif action == Action.POISON:
            health = self.agentInfo.getHealth()
            health = max(health - 25, 0)
            self.agentInfo.setHealth(health)
            isSuccessful = True

        self.updatePercept()    
        return isSuccessful, self.agentInfo
        
    def agentDoWithUi(self, action, score):
        self.current_step += 1
        isSuccessful = False
        isShootSuccess = False
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
                isSuccessful = True

            
        elif action == Action.TURN_RIGHT:
            direction = turnRight(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            isSuccessful = True
        
        elif action == Action.TURN_LEFT:
            direction = turnLeft(self.agentInfo.getDirection())
            self.agentInfo.setDirection(direction)
            isSuccessful = True
        
        elif action == Action.GRAB:
            x, y = self.agentInfo.getPosition()
            if self.map[x][y].hasObject(Environment.GOLD):
                self.map[x][y].removeObject(Environment.GOLD)
                self.agentInfo.adjustInventory(ItemType.GOLD, 1)
                isSuccessful = True
            elif self.map[x][y].hasObject(Environment.HEAL):
                self.map[x][y].removeObject(Environment.HEAL)
                self.agentInfo.adjustInventory(ItemType.HEAL, 1)
                isSuccessful = True
        
            
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
                    isSuccessful = True
                    isShootSuccess = True
                self.animateShoot(nextX, nextY)
                    
            
        elif action == Action.CLIMB:
            x, y = self.agentInfo.getPosition()
            if x == 0 and y == 0:
                isSuccessful = True
            
        
        elif action == Action.HEAL:
            if self.agentInfo.inventory[ItemType.HEAL] > 0:
                health = self.agentInfo.getHealth()
                health = min(health + 25, 100)
                self.agentInfo.setHealth(health)
                self.agentInfo.adjustInventory(ItemType.HEAL, -1)
                isSuccessful = True
        
        elif action == Action.POISON:
            health = self.agentInfo.getHealth()
            health = max(health - 25, 0)
            self.agentInfo.setHealth(health)
            isSuccessful = True

        self.explored.append(self.agentInfo.getPosition())
        self.updatePercept()   
        self.showMessageOnGui(action, score, isShootSuccess)
        return isSuccessful
    
    # MAP ON GUI
    def drawMap(self):
        self.canvas.delete("all")
        for i in range(self.height):
            for j in range(self.width):
                if not self.isvisible:
                    if (i, j) not in self.explored:
                        if i < self.height and j < self.width:
                            x1 = j * self.cellSize
                            y1 = i * self.cellSize
                            x2 = x1 + self.cellSize
                            y2 = y1 + self.cellSize
                            self.canvas.create_rectangle(x1, y1, x2, y2, fill="grey", outline="black")
                        continue
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
        # print(x, y)
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

    def showMessageOnGui(self, action, score, shootSuccess = None):
        actions = {
            Action.FORWARD: "Move forward",
            Action.TURN_RIGHT: "Turn right",
            Action.TURN_LEFT: "Turn left",
            Action.GRAB: "Grab",
            Action.SHOOT: "Shoot",
            Action.CLIMB: "Climb",
            Action.HEAL: "Heal"
        }
        if action != Action.POISON:
            self.outputFile += f'({self.agentInfo.getPosition()[0] + 1}, {self.agentInfo.getPosition()[1] + 1}): {actions[action]} - Score: {score} - Percepts: ['
        if action == Action.POISON:
            self.Gui.showMessage("You are poisoned and lost 25 health\n")
            return
        agentPos = self.agentInfo.getPosition()
        message = ""
        content = []
        message += "Action: "
        message += actions[action]
        message += "\n"
        message += "Current position: "
        message +=  str(self.convertMapPosition(agentPos[0], agentPos[1]))
        message += '\n'
        message += "Pecrepts: "
        percept = self.map[agentPos[0]][agentPos[1]].getPercept()
        if percept & Percept.STENCH:
            content.append("Stench")
        if percept & Percept.BREEZE:
            content.append("Breeze")
        if percept & Percept.SCREAM:
            content.append("Scream")
        if percept & Percept.WHIFF:
            content.append("Whiff")
        if percept & Percept.GLOW:
            content.append("Glow")
        if shootSuccess:
            content.append("Scream")
        message += ", ".join(content)
        self.outputFile += ', '.join(content)
        self.outputFile += ']\n'
        message += "\n"
        message += "Score: " + str(score) + "\n"
        message += "Health: "
        message += str(self.agentInfo.getHealth())
        message += "\n\n"
        self.Gui.showMessage(message)
        if(action != Action.SHOOT):
            self.reloadMap()


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
                self.reloadMap()
        moveArrow(0)
    

    def reloadMap(self):
        self.drawMap()