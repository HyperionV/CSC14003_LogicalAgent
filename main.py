def input(name):
    file = open(name, 'r')
    map = []
    for i in file:
        map.append(i.split('.'))
    return map

   