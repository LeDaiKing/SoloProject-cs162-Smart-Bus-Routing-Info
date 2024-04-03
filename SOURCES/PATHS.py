import json
from geojson import dump, Feature, FeatureCollection
class Path:

    def __init__(self, lat, lng, RouteId, RouteVarId):
        self.lat = lat
        self.lng = lng
        self.RouteId = RouteId
        self.RouteVarId = RouteVarId

    def getAttr(self, attr):
        return self.__dict__[attr]  
    
    def setAttr(self, attr, value):
        if attr in self.__dict__.keys():
            self.__dict__[attr] = value


class PathQuery:

    def __init__(self, filename = None):
        self.pathList = []
        if filename != None:
            self.loadFromFile(filename)

    def loadFromFile(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                data = json.loads(line)
                self.pathList.append(Path(data['lat'], data['lng'], data['RouteId'], data['RouteVarId']))

    def searchBy(self, **kwargs):
        searchedList = []
        for path in self.pathList:
            ok = True
            for key, value in kwargs.items():
                if path.getAttr(key) != value:
                    ok = False
            if ok:
                searchedList.append(path)
        return searchedList
    
    def outputAsCSV(self, queryList, filename):
        with open(filename, 'w') as file:
            file.write('lat, lng, RouteId, RouteVarId\n')
           
            for path in queryList:
                for key, value in path.__dict__.items():
                    if str(value) == str:
                        file.write(f"\"{value}\"")
                    else:
                        file.write(f"{value}")
                    
                    if key != 'RouteVarId':
                        file.write(', ')
                file.write('\n')

    def outputAsJSON(self, queryList, filename):
        with open(filename, 'w') as file:
            for path in queryList:
                file.write('{')
                for key, value in path.__dict__.items():
                    if str(value) == str:
                        file.write(f"\"{key}\": \"{value}\"")
                    else:
                        file.write(f"\"{key}\": {value}")
                    
                    if key != 'RouteVarId':
                        file.write(', ')
                file.write('}\n')

    def outputAsGeoJSON(self, queryList, filename):
        with open(filename, 'w') as file:
            features = []
            for path in queryList:
                features.append(Feature(geometry={"type": "LineString", "coordinates": [(x, y) for x, y in zip(path.getAttr('lng'), path.getAttr('lat'))]}, 
                                        properties={"RouteId": path.getAttr('RouteId'), "RouteVarId": path.getAttr('RouteVarId')}))
            feature_collection = FeatureCollection(features)
            dump(feature_collection, file)
                

