from enum import Enum, Flag, auto, IntEnum
class Action(Enum):
    FORWARD = auto()
    TURN_RIGHT = auto()
    TURN_LEFT = auto()
    GRAB = auto()
    SHOOT = auto()
    CLIMB = auto()
    HEAL = auto()
    
class ItemType(Enum):
    HEAL = auto()
    GOLD = auto()
    ARROW = auto()

class Environment(IntEnum):
    WUMPUS = 0
    PIT = 1
    POISON = 2
    GOLD = 3
    HEAL = 4
    AGENT = 5
    
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

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

ASSET_PATH = "assets/"
def getObjectsEnumArray(cellStr):
        cell_objects = []
        cell = cellStr
        # Handle multiple Wumpus (W)
        count_wumpus = cell.count('W')
        if count_wumpus > 0:
            cell_objects.extend([Environment.WUMPUS] * count_wumpus)
            cell = cell.replace('W', '')

        # Handle Poisonous Gas (P_G)
        if "P_G" in cell:
            cell_objects.append(Environment.POISON)
            cell = cell.replace('P_G', '')

        # Handle Healing Potions (H_P)
        if "H_P" in cell:
            cell_objects.append(Environment.HEAL)
            cell = cell.replace('H_P', '')

        # Handle Pit (P)
        if "P" in cell:
            cell_objects.append(Environment.PIT)
            cell = cell.replace('P', '')

        # Handle Gold (G)
        if "G" in cell:
            cell_objects.append(Environment.GOLD)
            cell = cell.replace('G', '')
        
        return cell_objects


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
    
def getAdjCell(x, y, dir):
    if dir == Direction.UP:
        return x - 1, y
    if dir == Direction.DOWN:
        return x + 1, y
    if dir == Direction.LEFT:
        return x, y - 1
    if dir == Direction.RIGHT:
        return x, y + 1
    
def getDirBetweenCells(x, y, u, v):
    ##### D  R  U   L
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    for k in range(4):
        new_x = dx[k] + x
        new_y = dy[k] + y
        if new_x == u and new_y == v:
            if k == 0:
                return Direction.DOWN
            elif k == 1:
                return Direction.RIGHT
            elif k == 2:
                return Direction.UP
            elif k == 3:
                return Direction.LEFT
    return -1

def getRotationOrder(initialDir, targetDir):
    res = []
    if initialDir == targetDir:
        return res
    def rotateRight(initialDir, targetDir):
        tmp = []
        while initialDir != targetDir:
            if initialDir == Direction.UP:
                initialDir = Direction.RIGHT
            elif initialDir == Direction.RIGHT:
                initialDir = Direction.DOWN
            elif initialDir == Direction.DOWN:
                initialDir = Direction.LEFT
            elif initialDir == Direction.LEFT:
                initialDir = Direction.UP
            tmp.append(Direction.RIGHT)
        return tmp
    def rotateLeft(initialDir, targetDir):
        tmp = []
        while initialDir != targetDir:
            if initialDir == Direction.UP:
                initialDir = Direction.LEFT
            elif initialDir == Direction.LEFT:
                initialDir = Direction.DOWN
            elif initialDir == Direction.DOWN:
                initialDir = Direction.RIGHT
            elif initialDir == Direction.RIGHT:
                initialDir = Direction.UP
            tmp.append(Direction.LEFT)
        return tmp
    listR = rotateRight(initialDir, targetDir)
    listL = rotateLeft(initialDir, targetDir)
    if len(listR) < len(listL):
        listL = listR
    return listL