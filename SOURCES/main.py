from PATHS import *
from STOPS import *
from VARS import *
from GRAPHS import *

t = 'SOURCES/input/'

ldk = Graph(t + 'stops.json', t +  'vars.json', t + 'paths.json')
ldk.dijkstra()
# ldk.findShortestPath('SOURCES/output/shortestPath', 732, 1294)
print('ok')
# with open('SOURCES/output/test.txt', 'w') as file:
#     start = 926
#     end = 3978
#     u = end
#     lng = []
#     lat = []
#     while u != -1:
#         file.write(f'{u}\n')
#         for id in range(len(ldk.trace[start][u][1]) - 1, 0, -1):
#             lng.append(ldk.trace[start][u][1][id][0])
#             lat.append(ldk.trace[start][u][1][id][1])
#             file.write(f'{ldk.trace[start][u][1][id][0]} {ldk.trace[start][u][1][id][1]}\n')
#         u = ldk.trace[start][u][0]
#     dka.pathList = [Path(lat, lng, 1, 1)]
#     dka.outputAsGeoJSON(dka.pathList, 'SOURCES/output/geotest.json')

# tt = ldk.counImStops()
# for i in range(0, 20):
#     print(tt[i])
