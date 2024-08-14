import program
from Utils import *
from pysat.solvers import Glucose3
    
class AgentProperties:
    def __init__(self, position, direction, health, point, inventory):
        self.position = position
        self.direction = direction
        self.health = health
        self.point = point
        self.inventory = inventory
        
    def __init__(self):
        self.position = (0, 0)
        self.direction = Direction.DOWN
        self.health = 100
        self.point = 0
        self.inventory = {
            ItemType.HEAL: 0,
            ItemType.GOLD: 0
        }
    
    def getPosition(self):
        return self.position
    
    def getDirection(self):
        return self.direction
    
    def getHealth(self):
        return self.health
    
    def getPoint(self):
        return self.point
    
    def setHealth(self, health):
        self.health = health

    def setPoint(self, point):
        self.point = point

    def setDirection(self, direction):
        self.direction = direction
    
    def setPosition(self, position):
        self.position = position

    def adjustInventory(self, item, amount):
        self.inventory[item] += amount
        
    def maxHealth(self):
        return min(100, self.health + self.inventory[ItemType.HEAL] * 25)
    
class KB:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.mapStatus = [{
            Environment.WUMPUS: Status.UNKNOWN,
            Environment.PIT: Status.UNKNOWN,
            Environment.POISON: Status.UNKNOWN,
            Environment.GOLD: Status.UNKNOWN,
            Environment.HEAL: Status.UNKNOWN
        } for _ in range(self.height) for _ in range(self.width)]
        self.percept = [Percept(0) for _ in range(self.height) for _ in range(self.width)]
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.solver = Glucose3()

    def update(self, percept, x, y):
        self.percept[x][y] = percept
        self.visited[x][y] = True
        # if not (percept & Percept.STENCH):
        #     self.mapStatus[x][y][Environment.WUMPUS] = Status.NONE
        # if not (percept & Percept.BREEZE):
        #     self.mapStatus[x][y][Environment.PIT] = Status.NONE
        # if not (percept & Percept.WHIFF):
        #     self.mapStatus[x][y][Environment.POISON] = Status.NONE
        # if not (percept & Percept.GLOW):
        #     self.mapStatus[x][y][Environment.HEAL] = Status.NONE
    
    def isVisited(self, x, y):
        return self.visited[x][y]
    
    def noWumpus(self, x, y):
        return self.infer(x, y)[Environment.WUMPUS] == Status.NONE

    def infer(self, x, y):
        # Infer the status of the objects in the cell (x, y)
        def literalToInt(x, y, obj):
            return (x * self.width + y) * len(Environment) + obj
        
        def intToLiteral(literal):
            obj = literal % len(Environment)
            literal //= len(Environment)
            y = literal % self.width
            literal //= self.width
            x = literal
            return (x, y, obj)
        
        def addClause(x, y):
            if self.percept[x][y] & Percept.STENCH:
                clause = []
                # If there is a stench in the cell, there is a wumpus in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        clause.append(literalToInt(x + i, y + j, Environment.WUMPUS))
                self.solver.add_clause(clause)
            else:
                # If there is no stench in the cell, there is no wumpus in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        self.solver.add_clause([-literalToInt(x + i, y + j, Environment.WUMPUS)])

            if self.percept[x][y] & Percept.BREEZE:
                clause = []
                # If there is a breeze in the cell, there is a pit in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        clause.append(literalToInt(x + i, y + j, Environment.PIT))
                self.solver.add_clause(clause)
            else:
                # If there is no breeze in the cell, there is no pit in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        self.solver.add_clause([-literalToInt(x + i, y + j, Environment.PIT)])

            if self.percept[x][y] & Percept.WHIFF:
                clause = []
                # If there is a whiff in the cell, there is a poison in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        clause.append(literalToInt(x + i, y + j, Environment.POISON))
                self.solver.add_clause(clause)
            else:
                # If there is no whiff in the cell, there is no poison in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        self.solver.add_clause([-literalToInt(x + i, y + j, Environment.POISON)])

            if self.percept[x][y] & Percept.GLOW:
                clause = []
                # If there is a glow in the cell, there is a heal potion in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        clause.append(literalToInt(x + i, y + j, Environment.HEAL))
                self.solver.add_clause(clause)
            else:
                # If there is no glow in the cell, there is no heal potion in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and x + i >= 0 and x + i < self.height and y + j >= 0 and y + j < self.width:
                        self.solver.add_clause([-literalToInt(x + i, y + j, Environment.HEAL)])
            
        self.solver = Glucose3()

        for i in range(self.height):
            for j in range(self.width):
                if self.visited[i][j]:
                    addClause(i, j)

        def getStatus(x, y, obj):
            canExist = self.solver.solve(assumptions=[literalToInt(x, y, obj)])
            canNotExist = self.solver.solve(assumptions=[-literalToInt(x, y, obj)])
            if canExist and canNotExist:
                return Status.UNKNOWN
            elif canExist:
                return Status.EXIST
            else:
                return Status.NONE
            
        self.mapStatus[x][y][Environment.WUMPUS] = getStatus(x, y, Environment.WUMPUS)
        self.mapStatus[x][y][Environment.PIT] = getStatus(x, y, Environment.PIT)
        self.mapStatus[x][y][Environment.POISON] = getStatus(x, y, Environment.POISON)
        self.mapStatus[x][y][Environment.GOLD] = getStatus(x, y, Environment.GOLD)
        self.mapStatus[x][y][Environment.HEAL] = getStatus(x, y, Environment.HEAL)

        return self.mapStatus[x][y]
    
# Environment.WUMPUS: Status.UNKNOWN,
# Environment.PIT: Status.UNKNOWN,
# Environment.POISON: Status.UNKNOWN,
# Environment.GOLD: Status.UNKNOWN,
# Environment.HEAL: Status.UNKNOWN

class Agent:
    # Hoang ganh
    def __init__(self, width, height, mainProg):
        self.kb = KB(width, height)
        self.width, self.height = width, height
        self.agentInfo = AgentProperties()
        self.agentMap = [[1e9 for y in range(height)] for x in range(width)]
        # self.kb.update(mainProg.map[1][1].percept, 1, 1)
        self.safeList = []
        self.poisonList = []
        self.actionList = []
        self.safeList.append((1, 1))
    def findPath(self, x, y, u, v):
        # BFS j day
        pass
    def inBound(self, x, y):
        if 0 < x and x <= self.width and 0 < y and y <= self.height:
            return True
        return False
    def isSafe(self, status):
        if not status[Environment.WUMPUS] and not status[Environment.PIT] and not status[Environment.POISON]:
            return True
        return False
    def isDoable(self, status):
        if status[Environment.POISON] and self.agentInfo.maxHealth > 25:
            return True
        return False
    def agentClear(self, mainProg):
        ax, ay = self.agentInfo.getPosition()
        percept = mainProg.map[ax][ay].percept
        status = self.kb.infer(ax, ay)
        self.safeList.remove((ax, ay))
        self.agentMap[ax][ay] = 0
        if status[Environment.POISON] == Status.EXIST:
            self.agentMap[ax][ay] = 1
        self.kb.update(mainProg.map[ax][ay].percept, ax, ay)
        # Grab gold
        while status[Environment.GOLD] == Status.EXIST:
            valid, newProperties = mainProg.agentDo(Action.GRAB)
            if not valid:
                break
            # Record action
            self.agentInfo = newProperties
        # Grab heal
        while status[Environment.HEAL] == Status.EXIST:
            valid, newProperties = mainProg.agentDo(Action.GRAB)
            if not valid:
                break
            # Record action
            self.agentInfo = newProperties
        # Kill all WUMPUS adjacent to agent
        if percept & Percept.STENCH:
            for k in range(4):
                susCellX, susCellY = getAdjCell(ax, ay, self.agentInfo.getDirection())
                if not self.inBound(susCellX, susCellY):
                    continue
                if not (self.kb.visited[susCellX][susCellY] and self.kb.noWumpus(susCellX, susCellY)):
                    while True:
                        valid, newProperties = mainProg.agentDo(Action.SHOOT)
                        self.agentInfo = newProperties
                        # Record action
                        if not valid: # wumpus scream
                            break
                if k == 3:
                    break
                valid, newProperties = mainProg.agentDo(Action.TURN_RIGHT)
                self.agentInfo = newProperties
                # Record action
            mainProg.updatePerceptInPos(ax, ay)
        # Move to adjacent
        safe = False
        for i, j in [(self.ax + 1, self.ay), (self.ax, self.ay + 1), (self.ax - 1, self.ay), (self.ax, self.ay - 1)]:
            if not self.inBound(i, j):
                continue
            status = self.kb.infer(i, j)
            if self.isSafe(status):
                safe = True
                if not self.kb.isVisited(i, j):
                    self.safeList.append((i, j))