from VARS import *
from STOPS import *
from PATHS import *
import heapq
from pyproj import Proj, transform
import json
import geojson
import random

from math import radians, sin, cos, sqrt, atan2

def distance(lng1, lat1, lng2, lat2):
    R = 6371.0
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000


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

        self.numVer = set([i.getAttr('StopId') for i in stopQuery.stopList])
        self.StopLngLat = {i.getAttr('StopId') : (i.getAttr('Lng'), i.getAttr('Lat')) for i in stopQuery.stopList}
        # self.numVer = max([i.getAttr('StopId') for i in stopQuery.stopList])
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
        # self.dist = [[10**9 for i in range(self.numVer + 1)] for j in range(self.numVer + 1)]
        # self.trace = [[-1 for i in range(self.numVer + 1)] for j in range(self.numVer + 1)]
        mx = 0.0
        for path in pathQuery.pathList:
            stopList = stopQuery.searchBy(RouteId = path.getAttr('RouteId'), RouteVarId = path.getAttr('RouteVarId'))
            
            temp = routeVarQuery.searchBy(RouteId = path.getAttr('RouteId'), RouteVarId = path.getAttr('RouteVarId'))[0]
            speed = temp.getAttr('Distance') / (temp.getAttr('RunningTime') * 60)
            
            prelng = -1
            prelat = -1
            preStopId = -1
            totalDis = 0
            id = 0
            total = 0
            listPath = []
            
            for lng, lat in zip(path.getAttr('lng'), path.getAttr('lat')):
                if prelng != -1:
                    totalDis += distance(prelng, prelat, lng, lat)
                    total  += distance(prelng, prelat, lng, lat)
                listPath.append((lng, lat))
                
                if id < len(stopList) and abs(stopList[id].getAttr('Lng') - lng) < 0.001997 and abs(stopList[id].getAttr('Lat') - lat) < 0.001997:
                    if preStopId != -1:
                        if totalDis < 0.1:
                            totalDis = distance(prelng, prelat, stopList[id].getAttr('Lng'), stopList[id].getAttr('Lat'))
                            total += totalDis

                        self.vertices[preStopId].append(((totalDis/speed, totalDis), stopList[id].getAttr('StopId')))
                        self.path[preStopId].append((listPath, path.getAttr('RouteId'), path.getAttr('RouteVarId')))
                        listPath = [(lng, lat)]

                    preStopId = stopList[id].getAttr('StopId')
                    id += 1
                    totalDis = 0
                    
                prelng = lng
                prelat = lat

            mx = max(abs(total - temp.getAttr('Distance'))/temp.getAttr('Distance')*100, mx)
            print(abs(total - temp.getAttr('Distance'))/temp.getAttr('Distance')*100)
            if id != len(stopList):
                print('ERROR')
                print(path.getAttr('RouteId'), path.getAttr('RouteVarId'))
                print(id)
                print(len(stopList))
            # print(totalDis)
        print('max',mx)   

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
                self.count[i] += self.cnt[start][i] * dp[i]


        # kk = [1115, 1239, 1152, 1393, 606, 603, 732, 271, 272, 174, 166, 35, 510, 1235, 1234, 1233, 169, 1155, 725, 440]
        # for u in kk:
        #     #u = random.choice(list(self.numVer))
        #     dem = 0
        #     for st in self.numVer:
        #         for v in self.numVer:
        #             if abs(self.dist[st][v] - self.dist[st][u] - self.dist[u][v]) <= 0.002:
        #                 dem += self.cnt[st][u]  * self.cnt[u][v]
        #     if dem != self.count[u]:
        #         print('ERROR')
        #         print(u)    
        #         print(dem)
        #         print(self.count[u])
        #         break
        #     else :
        #         print('OK')
        #         print(dem)

        ldk = []

        for key, value in self.count.items():
            ldk.append((value, key))

        ldk.sort(reverse = True)

        return ldk