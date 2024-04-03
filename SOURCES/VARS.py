import json

class RouteVar:
    
    def __init__(self, RouteId, RouteVarId, RouteVarName, RouteVarShortName, RouteNo, StartStop, EndStop, Distance, Outbound, RunningTime):
        self.RouteId = str(RouteId)
        self.RouteVarId = str(RouteVarId)
        self.RouteVarName = RouteVarName
        self.RouteVarShortName = RouteVarShortName
        self.RouteNo = RouteNo
        self.StartStop = StartStop
        self.EndStop = EndStop
        self.Distance = Distance
        self.Outbound = Outbound
        self.RunningTime = RunningTime

    def getAttr(self, attr):
        return self.__dict__[attr]
    
    def setAttr(self, attr, value):
        if attr in self.__dict__.keys():
            self.__dict__[attr] = value
    

class RouteVarQuery:

    def __init__(self, filename = None):
        self.RouteVarlist = []
        if filename !=  None:
            self.loadFromFile(filename)

    def loadFromFile(self, filename):
        with open(filename, "r", encoding = 'utf-8') as file:
            for line in file:
                data = json.loads(line)
                for i in data:
                    self.RouteVarlist.append(RouteVar(i['RouteId'], i['RouteVarId'], 
                                                      i['RouteVarName'], i['RouteVarShortName'], 
                                                      i['RouteNo'], i['StartStop'], i['EndStop'], 
                                                      i['Distance'], i['Outbound'], i['RunningTime']))
    
    def searchBy(self, **kwargs):
        searchedList = []
        for i in self.RouteVarlist:
            ok = True
            for key, value in kwargs.items():
                if i.getAttr(key) != value:
                    ok = False
            if ok:
                searchedList.append(i)
        
        return searchedList
   
    
    def outputAsCSV(self, queryList, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('RouteId, RouteVarId, RouteVarName, RouteVarShortName, RouteNo, StartStop, EndStop, Distance, Outbound, RunningTime\n')
            for i in queryList:
                for key, value in i.__dict__.items():
                    if type(value) == str:
                        file.write(f"\"{value}\"")
                    elif type(value) == bool:
                        file.write(f"{str(value).lower()}")
                    else:
                        file.write(f"{value}")
                    if key != 'RunningTime':
                        file.write(', ')
                file.write('\n')

    def outputAsJSON(self, queryList, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            for i in queryList:
                file.write('{')
                for key, value in i.__dict__.items():
                    if type(value) == str:
                        file.write(f"\"{key}\": \"{value}\"")
                    elif type(value) == bool:
                        file.write(f"\"{key}\": {str(value).lower()}")
                    else:
                        file.write(f"\"{key}\": {value}")
                    if key != 'RunningTime':
                        file.write(', ')
                file.write('}\n')