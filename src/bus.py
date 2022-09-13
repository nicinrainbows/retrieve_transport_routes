import pandas as pd
import numpy as np
import json
import requests
from landtransportsg import PublicTransport

class bus:

    '''
    Define a class to communicate with the citymapper API & LTA datamall API to retrieve GPS data
    for both bus service routes/paths and stops.

    Users will need to prepare their API credentials from LTA datamall before using this class.
    '''

    def __init__(self, API=None):
        self.API = API
        self.client = PublicTransport(self.API)
        self.bus_nums = []
        self.bus_ids = []
    
    def _retrieve_busnums(self):
        if self.bus_nums == []:
            for row in self.client.bus_services():
                self.bus_nums.append(row['ServiceNo'])
            self.bus_nums = list(set(self.bus_nums))
        else:
            print('Bus service number list has been retrieved before.')
    
    def _retrieve_busids(self):
        if self.bus_ids == []:
            for number in self.bus_nums:
                url = f'https://citymapper.com/api/2/findtransport?query=${number}&region_id=sg-singapore'
                r = requests.get(url=url)
                data = json.loads(r.content)
                busid = data['results'][1]['id']
                self.bus_ids.append(busid)
            self.bus_ids = list(set(self.bus_ids))
        else:
            print('Official bus id list has been retrieved before.')
    
    def _lat_lon_retrieval(self, temp):
        temp_lat = [x[0] for x in temp]
        temp_lon = [x[1] for x in temp]
        return temp_lat, temp_lon
    
    def _retrieve_busstops(self, stops_data):
        busstop_lat = []
        busstop_lon = []
        for k, v in stops_data.items():
            temp_lat, temp_lon = v['coords'][0], v['coords'][1]
            busstop_lat.append(temp_lat)
            busstop_lon.append(temp_lon)
        return busstop_lat, busstop_lon

    def _retrieve_buspath(self, path_data):
        buspath_lat = []
        buspath_lon = []
        for x in range(len(path_data)):
            temp_lat, temp_lon = self._lat_lon_retrieval(path_data[x]['path'])
            buspath_lat.extend(temp_lat)
            buspath_lon.extend(temp_lon)
        return buspath_lat, buspath_lon

    def _convert_to_df(self, route, path, lat, lon):
        df = pd.DataFrame(np.column_stack([route, path, lat, lon]),
                          columns=['route', 'path', 'lat', 'lon'])
        return df

    def _retrieve_bus_routes(self):
        if len(self.bus_ids) == 0:
            raise ValueError('Please retrieve bus ids first before running the function')
        lat, lon, route, path = [], [], [], []
        for busid in self.bus_ids:
            url = f'https://citymapper.com/api/1/routeinfo?route={busid}&region_id=sg-singapore&weekend=1&status_format=rich'
            r = requests.get(url=url)
            data = json.loads(r.content)
            if list(data.keys())[0] != 'error':
                busstop_lat, busstop_lon = self._retrieve_busstops(data['stops'])
                lat.extend(busstop_lat)
                lon.extend(busstop_lon)
                path += ['stop'] * len(busstop_lat)
                route += [busid] * len(busstop_lat)
                buspath_lat, buspath_lon = self._retrieve_buspath(data['routes'][0]['patterns'])
                lat.extend(buspath_lat)
                lon.extend(buspath_lon)
                path += ['stop'] * len(buspath_lat)
                route += [busid] * len(buspath_lat)
        if len(route) > 0:
            bus_df = self._convert_to_df(route, path, lat, lon)
            return bus_df
        else:
            raise ValueError('Could not retrieve any bus routes for the bus ids. Please check and try again.')