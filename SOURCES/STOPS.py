import json

class Stop:
    
    def __init__(self, StopId, Code, Name, StopType, Zone, Ward, AddressNo, Street,
                  SupportDisability, Status, Lng, Lat, Search, Routes, RouteId, RouteVarId):
        self.StopId = StopId
        self.Code = Code
        self._Name = Name
        self.StopType = StopType
        self.Zone = Zone
        self.Ward = Ward 
        self.AddressNo = AddressNo
        self.Street = Street
        self.SupportDisability = SupportDisability
        self.Status = Status
        self.Lng = Lng
        self.Lat = Lat
        self.Search = Search
        self.Routes = Routes
        self.RouteId = RouteId
        self.RouteVarId = RouteVarId

    def getAttr(self, attr):
        return self.__dict__[attr]
    
    def setAttr(self, attr, value):
        if attr in self.__dict__.keys():
            self.__dict__[attr] = value

class StopQuery:

    def __init__(self, filename = None):
        self.stopList = []
        if filename != None:
            self.loadFromFile(filename)

    def loadFromFile(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                data = json.loads(line)
                for stop in data['Stops']:
                    self.stopList.append(Stop(stop['StopId'], stop['Code'], stop['Name'], stop['StopType'],
                                              stop['Zone'], stop['Ward'], stop['AddressNo'], stop['Street'], 
                                              stop['SupportDisability'], stop['Status'], stop['Lng'], stop['Lat'],
                                                stop['Search'], stop['Routes'], data['RouteId'], data['RouteVarId']))
    
    def searchBy(self, **kwargs):
        searchedList = []
        for i in self.stopList:
            ok = True
            for key, value in kwargs.items():
                if i.getAttr(key) != value:
                    ok = False
            if ok:
                searchedList.append(i)
        return searchedList
    
    def outputAsCSV(self, queryList, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('StopId, Code, Name, StopType, Zone, Ward, AddressNo, Street, SupportDisability, Status, Lng, Lat, Search, Routes, RouteId, RouteVarId\n')
            for i in queryList:
                for key, value in i.__dict__.items():
                    if type(value) == str:
                        file.write(f"\"{value}\"")
                    elif value == None:
                        file.write('null')
                    else:
                        file.write(f"{value}")
                    if key != 'RouteVarId':
                        file.write(', ')
                file.write('\n')

   
    def outputAsJSON(self, queryList, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            for i in queryList:
                file.write('{')
                for key, value in i.__dict__.items():
                    if type(value) == str:
                        file.write(f"\"{key}\": \"{value}\"")
                    elif value == None:
                        file.write(f"\"{key}\": null")
                    else:
                        file.write(f"\"{key}\": {value}")
                    if key != 'RouteVarId':
                        file.write(', ')
                file.write('}\n')
                    