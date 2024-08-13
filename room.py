from enum import Enum

class Object(Enum):
    GOLD   = 'G'
    PIT    = 'P'
    WUMPUS = 'W'
    POISONOUS_GAS = 'P_G'
    HEALTH_POTION = 'H_P'
    EMPTY = '-'


class Room:
    def __init__(self, matrix_pos, map_size, objectsStrArray):
        self.matrix_pos = matrix_pos                                            # (0, 0) (0, 1) ... (9, 9)   (TL -> BR)
        self.map_pos = matrix_pos[1] + 1, map_size - matrix_pos[0]              # (1, 1) (1, 2) ... (10, 10) (BL -> TR)
        self.index_pos = map_size * (self.map_pos[1] - 1) + self.map_pos[0]     # 1 2 3 ... 99 100           (BL -> TR)
        self.map_size = map_size

        self.explored = False
        self.object = [0, 0, 0, 0, 0]  # [-G, -P, -W, -P_G, -H_P]
        self.init(objectsStrArray)



    def init(self, objectsStrArray):
        for obj in objectsStrArray:
            if obj == Object.GOLD.value:
                self.percept[0] = 1
            elif obj == Object.PIT.value:
                self.percept[1] = 1
            elif obj == Object.WUMPUS.value:
                self.percept[2] += 1
            elif obj == Object.POISONOUS_GAS.value:
                self.percept[3] = 1
            elif obj == Object.HEALTH_POTION.value:
                self.percept[4] = 1
            elif obj == Object.EMPTY.value:
                continue
            else:
                raise TypeError('Error: Cell.init')
            
    def isExistGold(self):
        return self.object[0] > 0
    
    def isExistPit(self):
        return self.object[1] > 0
    
    def isExistWumpus(self):
        return self.object[2] > 0
    
    def isExistPoisionousGas(self):
        return self.object[3] > 0

    def isExistHealthPotion(self):
        return self.object[4] > 0

    def getObjects(self):
        return self.object

    def grab_gold(self):
        self.object[0] = 0

    def useHP(self):
        self.object[3] = 0


    def kill_wumpus(self, cell_matrix, kb):
        # Delete Wumpus.
        if self.object[2] > 0:
            self.object[2] -= 1
            return True
        else:
            return False

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True

