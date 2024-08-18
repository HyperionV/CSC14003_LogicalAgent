from Utils import *
from pysat.solvers import Glucose3
from collections import deque
    
class AgentProperties:
    def __init__(self, position, direction, health, point, inventory):
        self.position = position
        self.direction = direction
        self.health = health
        self.point = point
        self.inventory = inventory
        
    def __init__(self):
        self.position = (9, 0)
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
        
    def getMaxHealth(self):
        return self.health + self.inventory[ItemType.HEAL] * 25
    
class KB:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.mapStatus = dict()
        for i in range(self.height):
            for j in range(self.width):
                self.mapStatus[(i, j)] = {
                    Environment.WUMPUS: Status.UNKNOWN,
                    Environment.PIT: Status.UNKNOWN,
                    Environment.POISON: Status.UNKNOWN,
                    Environment.HEAL: Status.UNKNOWN
                }
        self.percept = dict()
        for i in range(self.height):
            for j in range(self.width):
                self.percept[(i, j)] = Percept(0)
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.solver = Glucose3()
    
    def setVisit(self, u, v):
        self.visited[u][v] = 0

    def update(self, percept, x, y):
        self.percept[(x, y)] = percept
        self.visited[x][y] = True

    def isVisited(self, x, y):
        return self.visited[x][y]
    
    def noWumpus(self, x, y):
        return self.infer(x, y)[Environment.WUMPUS] == Status.NONE

    def infer(self, x, y):
        # Infer the status of the objects in the cell (x, y)
        def literalToInt(x, y, obj):
            return (x * self.width + y) * len(Environment) + obj + 1
        def intToLiteral(literal):
            literal -= 1
            obj = literal % len(Environment)
            literal //= len(Environment)
            y = literal % self.width
            literal //= self.width
            x = literal
            return (x, y, obj)
        
        def addClause(a, b):
            if self.percept[(a, b)] & Percept.STENCH:
                clause = []
                # If there is a stench in the cell, there is a wumpus in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        clause.append(literalToInt(a + i, b + j, Environment.WUMPUS))
                self.solver.add_clause(clause)
            else:
                # If there is no stench in the cell, there is no wumpus in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        self.solver.add_clause([-literalToInt(a + i, b + j, Environment.WUMPUS)])

            if self.percept[(a, b)] & Percept.BREEZE:
                clause = []
                # If there is a breeze in the cell, there is a pit in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        clause.append(literalToInt(a + i, b + j, Environment.PIT))
            else:
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        self.solver.add_clause([-literalToInt(a + i, b + j, Environment.PIT)])
            if self.percept[(a, b)] & Percept.WHIFF:
                clause = []
                # If there is a whiff in the cell, there is a poison in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        clause.append(literalToInt(a + i, b + j, Environment.POISON))
                self.solver.add_clause(clause)
            else:
                # If there is no whiff in the cell, there is no poison in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        self.solver.add_clause([-literalToInt(a + i, b + j, Environment.POISON)])

            if self.percept[(a, b)] & Percept.GLOW:
                clause = []
                # If there is a glow in the cell, there is a heal potion in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        clause.append(literalToInt(a + i, b + j, Environment.HEAL))
                self.solver.add_clause(clause)
            else:
                # If there is no glow in the cell, there is no heal potion in the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        self.solver.add_clause([-literalToInt(a + i, b + j, Environment.HEAL)])
            
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
            
        self.mapStatus[(x, y)][Environment.WUMPUS] = getStatus(x, y, Environment.WUMPUS)
        self.mapStatus[(x, y)][Environment.PIT] = getStatus(x, y, Environment.PIT)
        self.mapStatus[(x, y)][Environment.POISON] = getStatus(x, y, Environment.POISON)
        self.mapStatus[(x, y)][Environment.HEAL] = getStatus(x, y, Environment.HEAL)

        return self.mapStatus[(x, y)]
    
class Agent:
    def __init__(self, width, height):
        self.kb = KB(width, height)
        self.width, self.height = width, height
        self.agentInfo = AgentProperties()
        self.agentInfo.setPosition((9, 0))
        self.initialPos = (9, 0)
        self.agentMap = [[1e9 for y in range(height)] for x in range(width)]
        self.vis = [[0 for y in range(height)] for x in range(width)]
        self.agentMap[9][0] = 0
        self.safeList = []
        self.poisonList = []
        self.actionList = []
        self.safeList.append((9, 0))
        self.point = 0
    def addAction(self, action, gold = 0):
        if action == Action.SHOOT:
            self.point -= 100
        elif action == Action.CLIMB:
            self.point += 10
        elif action == Action.GRAB and gold > 0:
            self.point += 5000
        else:
            self.point -= 10
        self.actionList.append((action, self.point))
        
    def findHeuristic(self, x, y):
        dis = [[1e9 for y in range(self.height)] for x in range(self.width)]
        vis = [[0 for y in range(self.height)] for x in range(self.width)]
        dis[x][y] = 0
        dx = [1, 0, -1, 0]
        dy = [0, 1, 0, -1]
        queue = []
        queue.append((x, y))
        while len(queue) > 0:
            cur = queue.pop(0)
            if vis[cur[0]][cur[1]] != 0:
                continue
            vis[cur[0]][cur[1]] = 1
            for k in range(4):
                row = cur[0] + dx[k]
                col = cur[1] + dy[k]
                if not self.inBound(row, col):
                    continue
                if vis[row][col] > 0:
                    continue
                if self.agentMap[row][col] == 1e9:
                    continue
                if dis[cur[0]][cur[1]] + 1 < dis[row][col]:
                    dis[row][col] = dis[cur[0]][cur[1]] + 1
                    queue.append((row, col))
        return dis
    def findPath(self, x, y, u, v, findShortest = False):
        # BFS j day
        dq = deque()
        trace = [[(-1, -1) for y in range(self.height)] for x in range(self.width)]
        dis = [[1e9 for y in range(self.height)] for x in range(self.width)]
        heu = self.findHeuristic(x, y)
        vis = [[0 for y in range(self.height)] for x in range(self.width)]
        dis[x][y] = 0
        dx = [1, 0, -1, 0]
        dy = [0, 1, 0, -1]
        dq.append((x, y))
        while len(dq) > 0:
            cur = dq.popleft()
            if vis[cur[0]][cur[1]] != 0:
                continue
            vis[cur[0]][cur[1]] = 1
            for k in range(4):
                row = cur[0] + dx[k]
                col = cur[1] + dy[k]
                if not self.inBound(row, col):
                    continue
                if self.agentMap[row][col] == 1e9:
                    continue
                weight = self.agentMap[row][col]
                if dis[cur[0]][cur[1]] + weight < dis[row][col]:
                    dis[row][col] = dis[cur[0]][cur[1]] + weight
                    trace[row][col] = cur
                    if weight == 0:
                        dq.appendleft((row, col))
                    else:
                        dq.append((row, col))
        queue = []
        queue.append((x, y))
        vis = [[0 for y in range(self.height)] for x in range(self.width)]
        while len(queue) > 0:
            cur = queue.pop(0)
            if vis[cur[0]][cur[1]] != 0:
                continue
            vis[cur[0]][cur[1]] = 1
            for k in range(4):
                row = cur[0] + dx[k]
                col = cur[1] + dy[k]
                if not self.inBound(row, col):
                    continue
                if vis[row][col] > 0:
                    continue
                if self.agentMap[row][col] == 1e9:
                    continue
                weight = self.agentMap[row][col]
                if dis[cur[0]][cur[1]] + weight == dis[row][col]:
                    prev = trace[row][col]
                    queue.append((row, col))
                    if heu[prev[0]][prev[1]] > heu[cur[0]][cur[1]]:
                        trace[row][col] = cur
        if findShortest == True:
            curDis = 1e9
            res = -1
            tmpHeu = 1e9
            for safeCell in self.safeList:
                tmp = dis[safeCell[0]][safeCell[1]]
                if tmp < curDis:
                    curDis = tmp
                    res = safeCell
                    tmpHeu = 1e9
                elif tmp == curDis and heu[safeCell[0]][safeCell[1]] < tmpHeu:
                    tmpHeu = heu[safeCell[0]][safeCell[1]]
                    res = safeCell
            return res
        if vis[u][v] == 0:
            return -1
        row, col = u, v
        traceList = []
        cntPoison = 0
        # trace not include starting cell
        while (row, col) != (x, y):
            cntPoison += self.agentMap[row][col]
            traceList.append((row, col))
            prev = trace[row][col]
            row, col = prev[0], prev[1]
        traceList = traceList[::-1]
        return traceList, cntPoison
    def inBound(self, x, y):
        if 0 <= x and x < self.width and 0 <= y and y < self.height:
            return True
        return False
    def isSafe(self, status):
        if status[Environment.WUMPUS] == Status.NONE and status[Environment.PIT] == Status.NONE and status[Environment.POISON] == Status.NONE:
            return True
        return False
    def isDoable(self, status):
        if status[Environment.WUMPUS] == Status.NONE and status[Environment.PIT] == Status.NONE and not (status[Environment.POISON] == Status.NONE):
            return True
        return False
    def moveToAdjacentCell(self, fromCell, toCell, mainProg):
        from_x, from_y = fromCell
        to_x, to_y = toCell
        dir = getDirBetweenCells(from_x, from_y, to_x, to_y)
        rotationOrder = getRotationOrder(self.agentInfo.direction, dir)
        if len(rotationOrder) > 0:
            for newDir in rotationOrder:
                if newDir == Direction.RIGHT:
                    valid, info = mainProg.agentDo(Action.TURN_RIGHT)
                    self.agentInfo = info
                    self.addAction(Action.TURN_RIGHT)
                elif newDir == Direction.LEFT:
                    valid, info = mainProg.agentDo(Action.TURN_LEFT)
                    self.agentInfo = info
                    self.addAction(Action.TURN_LEFT)
        valid, info = mainProg.agentDo(Action.FORWARD)
        if not valid:
            print('moveToAdjacentCell error')
            exit(0)
        self.addAction(Action.FORWARD)
        self.agentInfo = info
    def revisit(self, adjList):
        for cell in adjList:
            x, y = cell
            self.kb.setVisit(x, y)
    def moveToCell(self, fromCell, toCell, mainProg, testRun = False):
        from_x, from_y = fromCell
        to_x, to_y = toCell
        res = self.findPath(from_x, from_y, to_x, to_y)
        if res == -1:
            print('    invalid tracing')
            for row in self.agentMap:
                print(row)
            return False # invalid
        traceList, poison = res
        
        maxHealth = self.agentInfo.getMaxHealth()
        healthUse = (int)(max(0, poison - self.agentInfo.getHealth()/25 + 1))
        cur = (from_x, from_y)
        if testRun == True:
            if maxHealth / 25 - poison <= 0:
                return -1
            return (maxHealth / 25 - poison) - 1
        for tar in traceList:
            if healthUse > 0:
                valid, info = mainProg.agentDo(Action.HEAL)
                self.agentInfo = info
                self.addAction(Action.HEAL)
                healthUse -= 1
            self.moveToAdjacentCell(cur, tar, mainProg)
            if mainProg.map[tar[0]][tar[1]].hasObject(Environment.POISON):
                valid, info = mainProg.agentDo(Action.POISON)
                self.agentInfo = info
                self.addAction(Action.POISON)
                if self.agentInfo.getHealth() == 0:
                    return False
            cur = tar
        return True # valid
    def checkEnd(self):
        if len(self.safeList) == 0 and len(self.poisonList) == 0:
            return True
        for i in range(self.width):
            for j in range(self.height):
                status = self.kb.infer(i, j)
                if status[Environment.WUMPUS] == Status.UNKNOWN or status[Environment.PIT] == Status.UNKNOWN or status[Environment.POISON] == Status.UNKNOWN:
                    return False
        return True
    def agentClear(self, mainProg):
        cnt = 0
        while True:
            cnt = cnt + 1
            if self.agentInfo.getHealth() <= 0:
                break
            ax, ay = self.agentInfo.getPosition()
            mainProg.updatePerceptInPos(ax, ay)
            percept = mainProg.map[ax][ay].getPercept()
            self.kb.update(percept, ax, ay)
            if (ax, ay) in self.poisonList:
                self.poisonList.remove((ax, ay))
                if mainProg.map[ax][ay].hasObject(Environment.POISON):
                    self.agentMap[ax][ay] = 1
                else:
                    self.agentMap[ax][ay] = 0
            elif (ax, ay) in self.safeList:
                self.safeList.remove((ax, ay)) 
                self.agentMap[ax][ay] = 0
            self.vis[ax][ay] = 1
            self.kb.update(mainProg.map[ax][ay].getPercept(), ax, ay)
            # Grab gold
            while mainProg.map[ax][ay].hasObject(Environment.GOLD):
                valid, newProperties = mainProg.agentDo(Action.GRAB)
                if not valid:
                    break 
                self.addAction(Action.GRAB, 1)
                self.agentInfo = newProperties
            # Grab heal
            while mainProg.map[ax][ay].hasObject(Environment.HEAL):
                valid, newProperties = mainProg.agentDo(Action.GRAB)
                if not valid:
                    break
                self.addAction(Action.GRAB)
                self.agentInfo = newProperties
                adjList = getAllAdjCell(ax, ay)
                self.revisit(adjList)
            # Kill all WUMPUS adjacent to agent
            if percept & Percept.STENCH:
                for k in range(4):
                    tmpPercept = mainProg.map[ax][ay].getPercept()
                    if not (tmpPercept & Percept.STENCH):
                        break
                    susCellX, susCellY = getAdjCell(ax, ay, self.agentInfo.getDirection())
                    if not self.inBound(susCellX, susCellY):
                        valid, newProperties = mainProg.agentDo(Action.TURN_RIGHT)
                        self.addAction(Action.TURN_RIGHT)
                        self.agentInfo = newProperties
                        continue
                    if not self.kb.noWumpus(susCellX, susCellY):
                        while True:
                            tmpPercept = mainProg.map[ax][ay].getPercept()
                            if not (percept & Percept.STENCH):
                                break
                            if self.vis[susCellX][susCellY] != 0 and self.agentMap[susCellX][susCellY] < 1e9:
                                break
                            valid, newProperties = mainProg.agentDo(Action.SHOOT)
                            self.addAction(Action.SHOOT)
                            self.agentInfo = newProperties
                            if not valid: # wumpus scream
                                break
                    if k == 3:
                        break
                    valid, newProperties = mainProg.agentDo(Action.TURN_RIGHT)
                    self.addAction(Action.TURN_RIGHT)
                    self.agentInfo = newProperties
                    mainProg.updatePerceptInPos(ax, ay)
                adjList = getAllAdjCell(ax, ay)
                self.revisit(adjList)
                mainProg.updatePerceptInPos(ax, ay)
                percept = mainProg.getPercept(ax, ay)
            tmpPercept = mainProg.getPercept(ax, ay)
            self.kb.update(tmpPercept, ax, ay)
    
            # Move to adjacent
            nextPos = -1
            for i in range(self.width):
                for j in range(self.height):
                    if not self.inBound(i, j):
                        continue
                    nextStatus = self.kb.infer(i, j)
                    if self.isSafe(nextStatus) and not ((i, j) in self.safeList) and self.vis[i][j] == 0:
                        self.safeList.append((i, j))
                        self.agentMap[i][j] = 0
                    elif nextStatus[Environment.POISON] == Status.EXIST:
                        self.agentMap[i][j] = 1
                    elif self.isDoable(nextStatus) and not ((i, j) in self.poisonList):
                        self.poisonList.append((i, j))
                        self.agentMap[i][j] = 1
            if self.checkEnd():
                # End game
                self.moveToCell((ax, ay), self.initialPos, mainProg)
                self.agentInfo.setPosition(self.initialPos)
                break
            safe = (len(self.safeList) > 0) # safe - unvisited cell that is "SAFE"
            if safe == False:
                nextPos = self.findPath(ax, ay, 0, 0, True)
                if nextPos != -1:
                    self.moveToCell((ax, ay), nextPos, mainProg)
                    self.agentInfo.setPosition(nextPos)
                # if not, find unvisited cell that has poison as the only threat
                else:
                    for poisonPos in self.poisonList:
                        if self.vis[poisonPos[0]][poisonPos[1]] == 0:
                            nextPos = poisonPos
                            break
                    # only go if enough health
                    remainingHealth = self.moveToCell((ax, ay), self.initialPos, mainProg, True)
                    if nextPos != -1 and (remainingHealth > 1):
                        self.moveToCell((ax, ay), nextPos, mainProg)
                        self.agentInfo.setPosition(nextPos)
                    else:
                        # End game
                        self.moveToCell((ax, ay), self.initialPos, mainProg)
                        self.agentInfo.setPosition(self.initialPos)
                        break
            else:
                nextPos = self.findPath(ax, ay, 0, 0, True)
                self.moveToCell((ax, ay), nextPos, mainProg)
                self.agentInfo.setPosition(nextPos)
        return self.actionList