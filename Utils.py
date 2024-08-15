from enum import Enum, Flag, auto
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

class Environment(Enum):
    WUMPUS = auto()
    PIT = auto()
    POISON = auto()
    GOLD = auto()
    HEAL = auto()
    AGENT = auto()
    
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

class AgentMap(Enum):
    SAFE = auto()
    UNSAFE = auto()
    DOABLE = auto()
    UNKNOWN = auto()

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
        return x + 1, y
    if dir == Direction.DOWN:
        return x - 1, y
    if dir == Direction.LEFT:
        return x, y - 1
    if dir == Direction.RIGHT:
        return x, y + 1