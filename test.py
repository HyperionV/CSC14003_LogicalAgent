from collections import deque
from queue import Queue

def inBound(x, y):
    width = height = 10
    if 0 <= x and x < width and 0 <= y and y < height:
        return True
    return False
def findPath(x, y, u, v, findShortest = False):
    width = height = 10
    # BFS j day
    # if x < 3 and y < 3:
    #     print('src, tar:', x, y, '   ', u, v)
    #     for row in agentMap:
    #         print(row)
    dq = deque()
    trace = [[(-1, -1) for y in range(height)] for x in range(width)]
    dis = [[1e9 for y in range(height)] for x in range(width)]
    heu = [[0 for y in range(height)] for x in range(width)]
    vis = [[0 for y in range(height)] for x in range(width)]
    agentMap = [[0 for y in range(height)] for x in range(width)]
    agentMap[2][9] = 1e9
    layer = [[-1 for y in range(height)] for x in range(width)]
    agentMap[5][4] = 1
    dis[x][y] = layer[x][y] = 0
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    dq.append((x, y))
    print('heu')
    for i in range(width):
        for j in range(height):
            heu[i][j] = (abs(x - i) + abs(y - j))
            print(heu[i][j], end = ' ')
        print()
    cntLayer = 1
    while len(dq) > 0:
        cur = dq.popleft()
        if vis[cur[0]][cur[1]] != 0:
            continue
        vis[cur[0]][cur[1]] = 1
        for k in range(4):
            row = cur[0] + dx[k]
            col = cur[1] + dy[k]
            if not inBound(row, col):
                continue
            if agentMap[row][col] == 1e9:
                continue
            weight = agentMap[row][col]
            if dis[cur[0]][cur[1]] + weight < dis[row][col]:
                dis[row][col] = dis[cur[0]][cur[1]] + weight
                trace[row][col] = cur
                if weight == 0:
                    dq.appendleft((row, col))
                else:
                    dq.append((row, col))
    queue = []
    queue.append((x, y))
    vis = [[0 for y in range(height)] for x in range(width)]
    print('trace before:')
    for row in trace:
        print(row)
    while len(queue) > 0:
        cur = queue.pop(0)
        if vis[cur[0]][cur[1]] != 0:
            continue
        vis[cur[0]][cur[1]] = 1
        for k in range(4):
            row = cur[0] + dx[k]
            col = cur[1] + dy[k]
            if not inBound(row, col):
                continue
            if vis[row][col] > 0:
                continue
            if agentMap[row][col] == 1e9:
                continue
            weight = agentMap[row][col]
            if dis[cur[0]][cur[1]] + weight == dis[row][col]:
                prev = trace[row][col]
                queue.append((row, col))
                print(' row, col:', row, col, '---', prev[0], prev[1], ' --- ', cur[0], cur[1])
                print('   consider:', heu[prev[0]][prev[1]], ' ', heu[cur[0]][cur[1]])
                if heu[prev[0]][prev[1]] > heu[cur[0]][cur[1]]:
                    print('     upd:', row, col, ' to:', prev)
                    trace[row][col] = cur
    print('trace:')
    for row in trace:
        print(row)
    print('dis:', vis[u][v])
    for i in range(width):
        for j in range(height):
            val = vis[i][j]
            if val == 1e9:
                val = 'X'
            print(val, end = ' ')
        print()
    if vis[u][v] == 0:
        return -1
    row, col = u, v
    traceList = []
    cntPoison = 0
    # trace not include starting cell
    cnt = 0
    while (row, col) != (x, y):
        cnt = cnt+1
        if cnt > 100:
            break
        cntPoison += agentMap[row][col]
        traceList.append((row, col))
        prev = trace[row][col]
        row, col = prev[0], prev[1]
    traceList = traceList[::-1]
    print('traceList:', traceList)
    return traceList, cntPoison

print('find')
findPath(3, 9, 1, 9)