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
        return min(100, self.health + self.inventory[ItemType.HEAL] * 25)
    
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

    def update(self, percept, x, y):
        self.percept[(x, y)] = percept
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
            return (x * self.width + y) * len(Environment) + obj + 1
        
        def intToLiteral(literal):
            literal -= 1
            obj = literal % len(Environment)
            literal //= len(Environment)
            y = literal % self.width
            literal //= self.width
            x = literal
            return (x, y, obj)
        
        def addClause(x, y):
            if self.percept[(x, y)] & Percept.STENCH:
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

            if self.percept[(x, y)] & Percept.BREEZE:
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

            if self.percept[(x, y)] & Percept.WHIFF:
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

            if self.percept[(x, y)] & Percept.GLOW:
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
            
        self.mapStatus[(x, y)][Environment.WUMPUS] = getStatus(x, y, Environment.WUMPUS)
        self.mapStatus[(x, y)][Environment.PIT] = getStatus(x, y, Environment.PIT)
        self.mapStatus[(x, y)][Environment.POISON] = getStatus(x, y, Environment.POISON)
        self.mapStatus[(x, y)][Environment.HEAL] = getStatus(x, y, Environment.HEAL)

        return self.mapStatus[(x, y)]
    
# Environment.WUMPUS: Status.UNKNOWN,
# Environment.PIT: Status.UNKNOWN,
# Environment.POISON: Status.UNKNOWN,
# Environment.GOLD: Status.UNKNOWN,
# Environment.HEAL: Status.UNKNOWN
class Agent:
    # Hoang ganh
    def __init__(self, width, height):
        self.kb = KB(width, height)
        self.width, self.height = width, height
        self.agentInfo = AgentProperties()
        self.agentInfo.setPosition((0, 0))
        self.agentMap = [[1e9 for y in range(height + 5)] for x in range(width + 5)]
        self.vis = [[0 for y in range(height + 5)] for x in range(width + 5)]
        self.agentMap[0][0] = 0
        self.safeList = []
        self.poisonList = []
        self.actionList = []
        self.safeList.append((0, 0))
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
    def findPath(self, x, y, u, v):
        # BFS j day
        # if x < 3 and y < 3:
        #     print('src, tar:', x, y, '   ', u, v)
        #     for row in self.agentMap:
        #         print(row)
        dq = deque()
        trace = [[(-1, -1) for y in range(self.height + 5)] for x in range(self.width + 5)]
        dis = [[1e9 for y in range(self.height + 5)] for x in range(self.width + 5)]
        vis = [[0 for y in range(self.height + 5)] for x in range(self.width + 5)]
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
                if self.agentMap[row][col] > 1:
                    continue
                weight = self.agentMap[row][col]
                if dis[cur[0]][cur[1]] + weight < dis[row][col]:
                    dis[row][col] = dis[cur[0]][cur[1]] + weight
                    trace[row][col] = cur
                    if weight == 0:
                        dq.appendleft((row, col))
                    else:
                        dq.append((row, col))
        if vis[u][v] == 0:
            return -1
        row, col = u, v
        traceList = []
        cntPoison = self.agentMap[row][col]
        # trace not include starting cell
        while (row, col) != (x, y):
            traceList.append((row, col))
            prev = trace[row][col]
            row, col = prev[0], prev[1]
            cntPoison += self.agentMap[prev[0]][prev[1]]
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
        # print('    initial dir:', self.agentInfo.getDirection())
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
        # print('    after:', self.agentInfo.getDirection(), '\n')
        valid, info = mainProg.agentDo(Action.FORWARD)
        if not valid:
            print('moveToAdjacentCell error')
            exit(0)
        self.addAction(Action.FORWARD)
        self.agentInfo = info
    def moveToCell(self, fromCell, toCell, mainProg):
        # print('    move to cell')
        from_x, from_y = fromCell
        to_x, to_y = toCell
        res = self.findPath(from_x, from_y, to_x, to_y)
        if res == -1:
            # print('    invalid tracing')
            return False # invalid
        traceList, poison = res
        maxHealth = self.agentInfo.getMaxHealth()
        if poison * 25 >= maxHealth:
            return False
        while self.agentInfo.getHealth() <= poison * 25:
            valid, info = mainProg.agentDo(Action.HEAL)
            if not valid:
                print('no heal available (how)')
            self.agentInfo = info
            self.addAction(Action.HEAL)
        # print('     traceList:', traceList)
        cur = (from_x, from_y)
        for tar in traceList:
            self.moveToAdjacentCell(cur, tar, mainProg)
            cur = tar
        return True # valid
    def agentClear(self, mainProg):
        while True:
            ax, ay = self.agentInfo.getPosition()
            print('ax, ay:', ax, ay)
            print('safeList:', self.safeList)
            percept = mainProg.map[ax][ay].percept
            status = self.kb.infer(ax, ay)
            if self.vis[ax][ay] == 0 and mainProg.map[ax][ay].hasObject(Environment.POISON):
                self.poisonList.remove((ax, ay))
                self.agentMap[ax][ay] = 1
            elif self.vis[ax][ay] == 0:
                self.safeList.remove((ax, ay)) 
                self.agentMap[ax][ay] = 0
            self.vis[ax][ay] = 1
            self.kb.update(mainProg.map[ax][ay].percept, ax, ay)
            # Grab gold
            while mainProg.map[ax][ay].hasObject(Environment.GOLD):
                valid, newProperties = mainProg.agentDo(Action.GRAB)
                if not valid:
                    break 
                self.addAction(Action.GRAB, 1)
                self.agentInfo = newProperties
            # Grab heal
            while status[Environment.HEAL] == Status.EXIST:
                valid, newProperties = mainProg.agentDo(Action.GRAB)
                if not valid:
                    break
                self.addAction(Action.GRAB)
                self.agentInfo = newProperties
            # Kill all WUMPUS adjacent to agent
            if percept & Percept.STENCH:
                for k in range(4):
                    susCellX, susCellY = getAdjCell(ax, ay, self.agentInfo.getDirection())
                    if not self.inBound(susCellX, susCellY):
                        continue
                    if not self.kb.noWumpus(susCellX, susCellY):
                        while True:
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
            tmpPercept = mainProg.getPercept(ax, ay)
            self.kb.update(tmpPercept, ax, ay)
            # print('percept:', tmpPercept)
            # Move to adjacent
            safe = False # safe - unvisited cell that is "SAFE"
            nextPos = -1
            for i, j in [(ax + 1, ay), (ax, ay + 1), (ax - 1, ay), (ax, ay - 1)]:
                if not self.inBound(i, j):
                    continue
                status = self.kb.infer(i, j)
                if self.isSafe(status) and not self.kb.isVisited(i, j):
                    safe = True
                    self.safeList.append((i, j))
                    self.agentMap[i][j] = 0
                    nextPos = (i, j)
                elif self.isDoable(status) and not self.kb.isVisited(i, j):
                    self.poisonList.append((i, j))
                    self.agentMap[i][j] = 1
            if safe == False:
                # find unvisited cell that is safe
                for safePos in self.safeList:
                    if self.vis[safePos[0]][safePos[1]] == 0:
                        nextPos = safePos
                        break
                if nextPos != -1:
                    self.moveToCell((ax, ay), nextPos, mainProg)
                    self.agentInfo.setPosition(nextPos)
                # if not, find unvisited cell that has poison as the only threat
                else:
                    for poisonPos in self.poisonList:
                        if self.vis[poisonPos[0]][poisonPos[1]] == 0:
                            nextPos = poisonPos
                            break
                    if nextPos != -1:
                        # print('   find poison cell:', nextPos)
                        self.moveToCell((ax, ay), nextPos, mainProg)
                        self.agentInfo.setPosition(nextPos)
                    else:
                        # End game
                        self.moveToCell((ax, ay), (0, 0), mainProg)
                        self.agentInfo.setPosition((0, 0))
                        break
            else:
                # if nextPos == -1:
                #     print('next pos:', nextPos)
                # else: 
                #     print('next pos:', nextPos[0], nextPos[1])
                self.moveToCell((ax, ay), nextPos, mainProg)
                self.agentInfo.setPosition(nextPos)
        for action in self.actionList:
            print(action)
        return self.actionList