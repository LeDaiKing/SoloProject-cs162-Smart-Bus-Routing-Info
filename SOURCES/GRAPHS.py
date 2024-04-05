from VARS import *
from STOPS import *
from PATHS import *
import heapq
from pyproj import Proj, Transformer
import json
import geojson
import random
from shapely.geometry import Point, LineString

from math import radians, sin, cos, sqrt, atan2

visited = {}
edge = {}
dp = {}

def dfs(u):
    global visited
    global edge
    global dp
    visited[u] = True
    dp[u] = 1
    for v in edge[u]:
        if visited[v] == False:
            dfs(v)
        dp[u] += dp[v]


class Graph:
    
    def __init__(self, filename1, filename2, filename3):
        stopQuery = StopQuery(filename1)
        routeVarQuery = RouteVarQuery(filename2)
        pathQuery = PathQuery(filename3)
        # pathQuery.pathList = pathQuery.searchBy(RouteId = '128', RouteVarId = '256')

        #inti pyproj
        inProj = Proj(init='epsg:4326')
        outProj = Proj(init='epsg:32648')
        self.trans = Transformer.from_proj(inProj, outProj, always_xy=True)
        self.retrans = Transformer.from_proj(outProj, inProj, always_xy=True)

        self.numVer = set([i.getAttr('StopId') for i in stopQuery.stopList])
        self.StopLngLat = {i.getAttr('StopId') : (i.getAttr('Lng'), i.getAttr('Lat')) for i in stopQuery.stopList}
        
        
        print(len(self.numVer))
        self.dist = {}
        self.trace = {}
        self.vertices = {}
        self.path = {}
        self.cnt = {}
        self.count = {}
        for i  in self.numVer:
            self.count[i] = 0
            self.vertices[i] = []
            self.path[i] =  []
            self.cnt[i] = {}
            self.dist[i] = {}
            self.trace[i] = {}
            for j in self.numVer:
                self.cnt[i][j] = 0
                self.dist[i][j] = 10**9
                self.trace[i][j] = (-1, ())
        mx = 0
        for path in pathQuery.pathList:
            total = 0
            self.linePath = [(x, y) for x, y in zip(path.getAttr('lng'), path.getAttr('lat'))]
            
            self.GeolinePath = LineString([(self.trans.transform(x, y)) for x, y in self.linePath])

            stopList = stopQuery.searchBy(RouteId = path.getAttr('RouteId'), RouteVarId = path.getAttr('RouteVarId'))
            
            temp = routeVarQuery.searchBy(RouteId = path.getAttr('RouteId'), RouteVarId = path.getAttr('RouteVarId'))[0]
            speed = temp.getAttr('Distance') / (temp.getAttr('RunningTime') * 60)
            prestop = None
            id = 0
            preid = 0
            for stop in stopList:
                lng, lat = stop.getAttr('Lng'), stop.getAttr('Lat')
                Dist = 0
                preid = id
                id = self.findNearestPoint(lng, lat, id)

                for i in range(preid, id):
                    Dist += self.distance(self.linePath[i][0], self.linePath[i][1], self.linePath[i + 1][0], self.linePath[i + 1][1])

                total += Dist
                if Dist < 0.1 and prestop != None:
                    print('ERROR')
                    print(prestop, stop.getAttr('StopId'), path.getAttr('RouteId'), path.getAttr('RouteVarId'))
                    Dist = self.distance(self.StopLngLat[prestop][0], self.StopLngLat[prestop][1], lng, lat)
                    print(Dist)

                if prestop != None:
                    self.vertices[prestop].append(((Dist / speed, Dist), stop.getAttr('StopId')))
                    self.path[prestop].append((self.linePath[preid: id + 1], path.getAttr('RouteId'), path.getAttr('RouteVarId')))
                    self.path[prestop][-1][0].append((lng, lat))

                prestop = stop.getAttr('StopId') 

            print((total - temp.getAttr('Distance')) / temp.getAttr('Distance')*100)
            mx = max(mx, abs(total - temp.getAttr('Distance')) / temp.getAttr('Distance')*100)
        print(mx, id, total)


    def distance(self, lng1, lat1, lng2, lat2):
        x1, y1 = self.trans.transform(lng1, lat1)
        x2, y2 = self.trans.transform(lng2, lat2)
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def findNearestPoint(self, lng, lat, id):
        minDist = 10**9
        res = None
        for i in range(id, len(self.linePath)):
            curDist = self.distance(lng, lat, self.linePath[i][0], self.linePath[i][1])
            if curDist < minDist:
                minDist = curDist
                res = i
        return res
        

    def dijkstra(self):
        for start in self.numVer:
            self.dist[start][start] = 0
            self.cnt[start][start] = 1
            pq = []
            heapq.heappush(pq, (0, start))
            while pq:
                dis, u = heapq.heappop(pq)
                if dis > self.dist[start][u]:
                    continue
                for (w, v), pa in zip(self.vertices[u], self.path[u]):
                    if dis + w[0] < self.dist[start][v]:
                        self.cnt[start][v] = self.cnt[start][u]
                        self.dist[start][v] = dis + w[0]
                        self.trace[start][v] = (u, pa)
                        heapq.heappush(pq, (dis + w[0], v))
                    elif dis + w[0] == self.dist[start][v]:
                        self.cnt[start][v] += self.cnt[start][u]

    def findShortestPath(self, filename, startStop, endStop):
        pass
        shortestPath = {'StartStopId': startStop, 'EndStopId': endStop, 'distance' : 0, 'runningTime' : self.dist[startStop][endStop],'StopIds': [], 'Paths': []}
        feature = []

        u = endStop
        while u != -1:
            temp = self.trace[startStop][u]
            shortestPath['StopIds'].append(u)
            feature.append(Feature(geometry={"type": "Point", "coordinates": [self.StopLngLat[u][0], self.StopLngLat[u][1]]}, properties={"StopId": u}))
       
            if u != startStop:
                shortestPath['Paths'].append({'lat': [lat[1] for lat in temp[1][0]], 'lng': [lng[0] for lng in temp[1][0]], 'RouteId': temp[1][1], 'RouteVarId': temp[1][2]})
                feature.append(Feature(geometry={"type": "LineString", "coordinates": temp[1][0]}, properties={"RouteId": temp[1][1], "RouteVarId": temp[1][2]}))
             
            u = temp[0]

        shortestPath['StopIds'] = shortestPath['StopIds'][::-1]
        shortestPath['Paths'] = shortestPath['Paths'][::-1]

        with open(filename + '.json', 'w') as file:
            file.write(json.dumps(shortestPath, separators=(', ', ' : ')))

        with open(filename + '.geojson', 'w') as file:
            feature_collection = FeatureCollection(feature)
            dump(feature_collection, file)

        


    def counImStops(self):
        
        global visited
        global edge
        global dp
        

        for start in self.numVer:

            for i in self.numVer:
                dp[i] = 0
                edge[i] = []
                visited[i] = False
           
           
           # build dag
            for i in self.numVer: 
                for j in self.vertices[i]:
                    if self.dist[start][i] + j[0][0] == self.dist[start][j[1]]:
                        edge[i].append(j[1])
            
            #count paths start from u to other vertice
            
            #topo list and dp
            for i in self.numVer:
                if visited[i] == False:
                    dfs(i)

            for i in self.numVer:
                self.count[i] +=  dp[i]

        ldk = []

        for key, value in self.count.items():
            ldk.append((value, key))

        ldk.sort(reverse = True)

        return ldk