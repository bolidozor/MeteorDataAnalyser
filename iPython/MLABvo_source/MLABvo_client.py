import requests
import datetime

class RTbolidozor():
    def __init__(self):
        self.server_mvo = 'http://api.vo.astro.cz/bolidozor/'
        self.station_id = None
        self.station_name = None
        self.station_param = None
    
    def _makeRequest(self, url, arguments=None, debug = False):
        if debug: print(self.server_mvo+url, arguments)
        return requests.get(self.server_mvo+url, params=arguments).json()
    
    def getStations(self, id = None, name = None, all=False):
        if id and name:
            raise Exception("Can not be set 'id' and 'name' parametr together.")
        elif all:
            stations = self._makeRequest('getStation/', {'all':all})
        else:
            stations = self._makeRequest('getStation/', {'id':id, 'name':name})
        return stations['stations']
    
    def setStation(self, station):
        if type(station) is list:
            station = station[0]
        self.station_id = station['id']
        self.station_name = station['namesimple']
        self.station_param = station
        return True
    
    def getSnapshot(self, station = None, date_from = None, date_to = datetime.datetime.now()):
        #TODO: pokud je stanice text, tak ji vyhledat v db (pomoci getStation) a nastavit (self.setStation())
        
        if station and not type(station) == int: 
            raise Exception("argument 'station' must be integer or None (not %s). It presents 'station_id'" %(type(station)))
        
        if station == None:
            station = self.station_id
        
        stations = self._makeRequest('getSnapshot/', {'station_id':station, 'date_from':date_from, 'date_to': date_to}, debug=False)
        return stations['snapshots']