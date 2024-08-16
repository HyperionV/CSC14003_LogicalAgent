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
        # pass
        # print(f'set {u}, {v} to 0')
        self.visited[u][v] = 0

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

        # if x == 6 and y == 3:
        #     # print percepts
        #     for i in range(self.height):
        #         for j in range(self.width):
        #             if not self.visited[i][j]:
        #                 print('(' + str(i) + ', ' + str(j) + ') ?', end=' ')
        #             elif self.percept[(i, j)] & Percept.BREEZE:
        #                 print('(' + str(i) + ', ' + str(j) + ') 1', end=' ')
        #             else:
        #                 print('(' + str(i) + ', ' + str(j) + ') 0', end=' ')
        #         print()
        
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
                if a == 6 and b == 3:
                    print('percept Breeze')
                # If there is a breeze in the cell, there is a pit in one of the adjacent cells
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        if a == 6 and b == 3:
                            print(f'breeze in {a + i}, {b + j}')
                        clause.append(literalToInt(a + i, b + j, Environment.PIT))
                # if x == 6 and y == 3:
                #     print('  add clause:', clause)
            else:
                # If there is no breeze in the cell, there is no pit in the adjacent cells
                # if a == 6 and b == 3:
                #     print('percept NO Breeze')
                for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if i * j == 0 and a + i >= 0 and a + i < self.height and b + j >= 0 and b + j < self.width:
                        # if a == 6 and b == 3:
                        #     print(f'NO breeze in {a + i}, {b + j}')
                        self.solver.add_clause([-literalToInt(a + i, b + j, Environment.PIT)])
                # if x == 6 and y == 3:
                #     print('  add clause:', [-literalToInt(a + i, b + j, Environment.PIT) for i, j in [(-1, 0), (1, 0), (0, -1), (0, 1)]])

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
                    # if x == 6 and y == 3:
                    #     print('infer 6, 3:', i, j)
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
    def findPath(self, x, y, u, v, findShortest = False):
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
                if not self.inBound(row, col):
                    continue
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
        if findShortest == True:
            curDis = 1e9
            res = -1
            for safeCell in self.safeList:
                if self.vis[safeCell[0]][safeCell[1]] != 0:
                    continue
                tmp = dis[safeCell[0]][safeCell[1]]
                if tmp < curDis:
                    curDis = tmp
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
    def revisit(self, adjList):
        for cell in adjList:
            x, y = cell
            self.kb.setVisit(x, y)
    def moveToCell(self, fromCell, toCell, mainProg, testRun = False):
        # print('    move to cell')
        from_x, from_y = fromCell
        to_x, to_y = toCell
        res = self.findPath(from_x, from_y, to_x, to_y)
        if res == -1:
            print('    invalid tracing')
            for row in self.agentMap:
                print(row)
            return False # invalid
        traceList, poison = res
        print('poison:', poison)
        maxHealth = self.agentInfo.getMaxHealth()
        # if poison * 25 >= maxHealth:
        #     return False
        healthUse = max(0, poison - maxHealth / 25 + 1)
        cur = (from_x, from_y)
        if testRun == True:
            if maxHealth / 25 - poison <= 0:
                return -1
            return (maxHealth / 25 - poison) - 1
        print(f' from {from_x}, {from_y} - to {to_x}, {to_y}')
        for tar in traceList:
            print(f'  move to ({tar[0]}, {tar[1]}) - remaining health:', self.agentInfo.getHealth())
            if healthUse > 0:
                valid, info = mainProg.agentDo(Action.HEAL)
                self.agentInfo = info
                self.addAction(Action.HEAL)
                healthUse -= 1
            self.moveToAdjacentCell(cur, tar, mainProg)
            # mapObject = mainProg.getObject(tar[0], tar[1])
            if mainProg.map[tar[0]][tar[1]].hasObject(Environment.POISON):
                valid, info = mainProg.agentDo(Action.POISON)
                self.agentInfo = info
                self.addAction(Action.POISON)
                if self.agentInfo.getHealth() == 0:
                    return False
            cur = tar
        return True # valid
    def agentClear(self, mainProg):
        cnt = 0
        while True:
            cnt = cnt + 1
            if self.agentInfo.getHealth() <= 0:
                # print('chet me m roi')
                break
            ax, ay = self.agentInfo.getPosition()
            # print('safeList:', self.safeList)
            # print('poisonList:', self.poisonList)
            mainProg.updatePerceptInPos(ax, ay)
            percept = mainProg.map[ax][ay].getPercept()
            self.kb.update(percept, ax, ay)
            status = self.kb.infer(ax, ay)
            print((f'\nax, ay: {ax}, {ay}, {self.agentInfo.getDirection()}, {self.agentInfo.getHealth()}'))
            # print('cell percept:', percept)

            # with open("output.txt", "a") as file:
            #     file.write(f'step {cnt}:\n')
            #     file.write(f'ax, ay: {ax}, {ay}, {self.agentInfo.getDirection()}' + '\n')
            #     for row in self.agentMap:
            #         file.write(" ".join(map(str, row)) + '\n\n')

            # print('status:', status)
            if self.vis[ax][ay] == 0 and (ax, ay) in self.poisonList:
                self.poisonList.remove((ax, ay))
                if mainProg.map[ax][ay].hasObject(Environment.POISON):
                    self.agentMap[ax][ay] = 1
                else:
                    self.agentMap[ax][ay] = 0
            elif self.vis[ax][ay] == 0 and (ax, ay) in self.safeList:
                # if not self.isSafe(status) and not self.isDoable(status):
                #     print('Status:', status, ax, ay)
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
            
            # if ax == 4 and ay == 7:
            #     status6_3 = self.kb.infer(6, 3)
            #     print('kill wumpus:', ax, ay, self.agentInfo.getHealth(), self.isSafe(status6_3), self.agentMap[6][3], status6_3, self.kb.visited[6][3], self.kb.visited[6][2])
            #     print('map percept:', tmpPercept)
            

            self.kb.update(tmpPercept, ax, ay)
            
            # if ax == 4 and ay == 7:
            #     status6_3 = self.kb.infer(6, 3)
            #     print('updated logic:', ax, ay, self.agentInfo.getHealth(), self.isSafe(status6_3), self.agentMap[6][3], status6_3, self.kb.visited[6][3], self.kb.visited[6][2])
            # Move to adjacent
            safe = False # safe - unvisited cell that is "SAFE"
            nextPos = -1
            for i, j in [(ax + 1, ay), (ax, ay + 1), (ax - 1, ay), (ax, ay - 1)]:
                if not self.inBound(i, j):
                    continue
                # print(' ax, ay:', ax, ay)
                # print('  adj:', i, j)
                nextStatus = self.kb.infer(i, j)
                if self.isSafe(nextStatus) and not self.kb.isVisited(i, j) and not ((i, j) in self.safeList):
                    safe = True
                    self.safeList.append((i, j))
                    self.agentMap[i][j] = 0
                    nextPos = (i, j)
                    # print('  safe:', i, j)
                elif self.isDoable(nextStatus) and not self.kb.isVisited(i, j):
                    self.poisonList.append((i, j))
                    self.agentMap[i][j] = 1
            if safe == False:
                # find unvisited cell that is safe
                nextPos = self.findPath(ax, ay, 0, 0, True)
                # for safePos in self.safeList:
                #     if self.vis[safePos[0]][safePos[1]] == 0:
                #         nextPos = safePos
                #         break
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
                    if nextPos != -1 and (self.moveToCell((ax, ay), nextPos, mainProg, True) > 1):
                        # print('   find poison cell:', nextPos)
                        # testRun = self.moveToCell((ax, ay), nextPos, mainProg, True)
                        self.moveToCell((ax, ay), nextPos, mainProg)
                        self.agentInfo.setPosition(nextPos)
                    else:
                        # End game
                        print('end game\n')
                        self.moveToCell((ax, ay), self.initialPos, mainProg)
                        self.agentInfo.setPosition(self.initialPos)
                        break
            else:
                # if nextPos == -1:
                #     print('next pos:', nextPos)
                # else: 
                #     print('next pos:', nextPos[0], nextPos[1])
                self.moveToCell((ax, ay), nextPos, mainProg)
                self.agentInfo.setPosition(nextPos)
        # for action in self.actionList:
        #     print(action)
        for i in range(self.width):
            for j in range(self.height):
                print(self.agentMap[i][j], end = ' ')
            print()
        print('safeList:', self.safeList)
        return self.actionList