
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
    
class Agent:
    # Hoang ganh
    def __init__(self, map, kb):
        self.kb = kb
        self.agentInfo = AgentProperties()
        pass