import pandas as pd
import numpy as np
import json
import requests

class mrt:
    
    '''
    Define a class to communicate with the citymapper API to retrieve GPS data for both
    MRT stops and paths.

    Update the self.route_ids for when there are new MRT lines available.
    '''

    def __init__(self, route_ids=None):
        if route_ids is None:
            self.route_ids = [
                'SingaporeMRTCircleLine',
                'SingaporeMRTDowntownLine',
                'SingaporeMRTEastwestLine',
                'SingaporeMRTNortheastLine',
                'SingaporeMRTNorthsouthLine',
                'CM_SingaporeMRT_tel',
                'SingaporeLRTBukitPanjangLine',
                'SingaporeLRTPunggolLineEastLoop',
                'SingaporeLRTPunggolLineWestLoop',
                'SingaporeLRTSengkangLineEastLoop',
                'SingaporeLRTSengkangLineWestLoop'
            ]
        else:
            self.route_ids = route_ids
    
    def _lat_lon_retrieval(self, temp):
        temp_lat = [x[0] for x in temp]
        temp_lon = [x[1] for x in temp]
        return temp_lat, temp_lon
    
    def _convert_to_df(self, route, path, lat, lon):
        df = pd.DataFrame(np.column_stack([route, path, lat, lon]),
                          columns=['route', 'path', 'lat', 'lon'])
        return df
    
    def _retrieve_mrt_routes(self):
        lat, lon, route, path = [], [], [], []
        for route_id in self.route_ids:
            url = 'https://citymapper.com/api/2/routeinfo'
            params = {'route_ids':route_id, 'region_id':'sg-singapore',
                      'weekend':1, 'status_format':'rich'}
            r = requests.get(url=url, params=params)
            data = json.loads(r.content)
            if list(data.keys())[0] != 'error':
                temp_latlon = data['routes'][0]['patterns'][0]['path']
                temp_lat, temp_lon = self._lat_lon_retrieval(temp_latlon)
                lat.extend(temp_lat)
                lon.extend(temp_lon)
                path += ['path'] * len(temp_latlon)
                temp_stops = []
                for k, v in data['stops'].items():
                    temp_stops.append(v['coords'])
                temp_lat, temp_lon = self._lat_lon_retrieval(temp_stops)
                lat.extend(temp_lat)
                lon.extend(temp_lon)
                path += ['stop'] * len(temp_stops)
                route += [route_id] * (len(temp_latlon) + len(temp_stops))
        if len(lat) > 0:
            mrt_df = self._convert_to_df(route, path, lat, lon)
            return mrt_df
        else:
            raise ValueError('Could not retrieve any mrt routes for the given mrt route ids. Please check and try again.')