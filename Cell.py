from Utils import Environment, Percept

class Cell:
    def __init__(self):
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
    
    def addObjects(self, objects):
        for obj in objects:
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