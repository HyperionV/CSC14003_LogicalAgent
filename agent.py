from enum import Enum, Flag, auto
from flag import Flag

from pysat.solvers import Glucose3

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

def turnRight(direction):
    if direction == Direction.UP:
        return Direction.RIGHT
    elif direction == Direction.RIGHT:
        return Direction.DOWN
    elif direction == Direction.DOWN:
        return Direction.LEFT
    elif direction == Direction.LEFT:
        return Direction.UP

def turnLeft(direction):
    if direction == Direction.UP:
        return Direction.LEFT
    elif direction == Direction.LEFT:
        return Direction.DOWN
    elif direction == Direction.DOWN:
        return Direction.RIGHT
    elif direction == Direction.RIGHT:
        return Direction.UP

class Action(Enum):
    FORWARD = auto()
    TURN_RIGHT = auto()
    TURN_LEFT = auto()
    GRAB = auto()
    SHOOT = auto()
    CLIMB = auto()
    HEAL = auto()

class Environment(Enum):
    WUMPUS = auto()
    PIT = auto()
    POISON = auto()
    GOLD = auto()
    HEAL = auto()

class Percept(Flag):
    STENCH = auto()
    BREEZE = auto()
    SCREAM = auto()
    WHIFF = auto()
    GLOW = auto()

class Status(Enum):
    NONE = auto()
    EXIST = auto()
    UNKNOWN = auto()

class Cell:
    def __init__(self, objects):
        self.obj = {
            Environment.WUMPUS: 0,
            Environment.PIT: 0,
            Environment.POISON: 0,
            Environment.GOLD: 0,
            Environment.HEAL: 0
        }
        self.percept = Percept(0)

    def addObject(self, obj):
        self.obj[obj] += 1
    
    def removeObject(self, obj):
        self.obj[obj] -= 1
    
    def hasObject(self, obj):
        return self.obj[obj] > 0
    
    def getObjects(self):
        return self.obj
    
    def updatePercept(self, percept):
        self.percept = percept

    # def removePercept(self, percept):
    #     self.percept &= ~percept

    def getPercept(self):
        return self.percept
    


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[Cell() for _ in range(width)] for _ in range(height)]

    def readMap(self, filename):
        pass

    def getMap(self):
        return self.map
    
    def updatePercept(self):
        # Update percept for each cell according to the objects in the adjacent cells
        for i in range(self.height):
            for j in range(self.width):
                percept = Percept(0)
                for x in range(-1, 2):
                    for y in range(-1, 2):
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
    
class KB:
    def __init__(self, map):
        self.mapStatus = [{
            Environment.WUMPUS: Status.UNKNOWN,
            Environment.PIT: Status.UNKNOWN,
            Environment.POISON: Status.UNKNOWN,
            Environment.GOLD: Status.UNKNOWN,
            Environment.HEAL: Status.UNKNOWN
        } for _ in range(map.height) for _ in range(map.width)]
        self.percept = [Percept(0) for _ in range(map.height) for _ in range(map.width)]
        self.visited = [[False for _ in range(map.width)] for _ in range(map.height)]
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
            return (x * self.map.width + y) * len(Environment) + obj
        
        def intToLiteral(literal):
            obj = literal % len(Environment)
            literal //= len(Environment)
            y = literal % self.map.width
            literal //= self.map.width
            x = literal
            return (x, y, obj)
        
        def addClause(x, y):
            if self.percept[x][y] & Percept.STENCH:
                clause = []
                # If there is a stench in the cell, there is a wumpus in one of the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            clause.append(literalToInt(x + i, y + j, Environment.WUMPUS))
                self.solver.add_clause(clause)
            else:
                # If there is no stench in the cell, there is no wumpus in the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            self.solver.add_clause([-literalToInt(x + i, y + j, Environment.WUMPUS)])

            if self.percept[x][y] & Percept.BREEZE:
                clause = []
                # If there is a breeze in the cell, there is a pit in one of the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            clause.append(literalToInt(x + i, y + j, Environment.PIT))
                self.solver.add_clause(clause)
            else:
                # If there is no breeze in the cell, there is no pit in the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            self.solver.add_clause([-literalToInt(x + i, y + j, Environment.PIT)])

            if self.percept[x][y] & Percept.WHIFF:
                clause = []
                # If there is a whiff in the cell, there is a poison in one of the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            clause.append(literalToInt(x + i, y + j, Environment.POISON))
                self.solver.add_clause(clause)
            else:
                # If there is no whiff in the cell, there is no poison in the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            self.solver.add_clause([-literalToInt(x + i, y + j, Environment.POISON)])

            if self.percept[x][y] & Percept.GLOW:
                clause = []
                # If there is a glow in the cell, there is a heal potion in the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            clause.append(literalToInt(x + i, y + j, Environment.HEAL))
                self.solver.add_clause(clause)
            else:
                # If there is no glow in the cell, there is no heal potion in the adjacent cells
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if i * j == 0 and x + i >= 0 and x + i < self.map.height and y + j >= 0 and y + j < self.map.width:
                            self.solver.add_clause([-literalToInt(x + i, y + j, Environment.HEAL)])
            
        self.solver = Glucose3()

        for i in range(self.map.height):
            for j in range(self.map.width):
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
        pass
