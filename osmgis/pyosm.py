#!/usr/bin/env python
import pdb
import os
import sys
from collections import defaultdict
import requests
import matplotlib.pyplot as plt
from pandas import DataFrame, Series, rolling_apply, np
from lxml import etree, objectify

class WayObj(DataFrame):
    def __init__(self,data,*args,**kwargs):
        DataFrame.__init__(self,data,*args,**kwargs)

    def distance_calc(self,window,freq):
        self['distance'] = rolling_distance(self,window,freq)
        
    def slice(self,n=10):
        lat_mn = self.lat.min()
        lat_mx = self.lat.max()
        lon_mn = self.lon.min()
        lon_mx = self.lon.max()
        lat_d = (lat_mx-lat_mn)/n
        lon_d = (lon_mx-lon_mn)/n

    def __sub__(self,way):
        return object.__sub__(self,way)

class Mapable(DataFrame):
    _streets = defaultdict(list)
    def __init__(self,x,y,d=0.025,verbose=False,**kwargs):
        xml = osm_xml_download(x,y,d,verbose)
        osm = etree.fromstring(xml.encode('utf-8'))
        data = [Series({key:value for key,value in node.attrib.items() if key in ['lat','lon']},name=node.attrib['id'])  for node in osm.findall('node')]
        DataFrame.__init__(self,data,dtype=float,**kwargs)
        self.street_setter(osm.findall('way'))
        self.index = self.index.astype(int)

    def street_getter(self,ref,distance=False):
        nodes = self._streets[ref]
        way = self.loc[nodes]
        if distance:
            way['distance'] = rolling_distance(way,2)
        return way

    def istreet_getter(self,i,distance=False):
        ref = list(self.streets.keys())[i]
        return self.street_getter(ref,distance)

    def length(self,way):
        """returns the length of streets, segment at a time"""
        return rolling_apply(2,distance)

    @property
    def streets(self):
        return self._streets

    def street_setter(self,ways):
        for way in ways:
            self._streets[int(way.attrib['id'])] += [int(i.attrib['ref']) for i in way.findall('nd') if i.attrib.get('ref')]

    def plot_streets(self):
        plt.figure()
        for ref in self._streets:
            way = self.street_getter(ref)
            plt.plot(way['lat'],way['lon'])

def osm_xml_download(x,y,d=0.025,verbose=False):
    """downloads the xml output from openstreetmap.org"""
    url = 'http://api.openstreetmap.org/api/0.6/map'
    cap = requests.get('http://api.openstreetmap.org/api/capabilities')
    if verbose:
        print(cap.text)
    origin = np.array([x,y])
    params = (origin-d).tolist()+(origin+d).tolist()
    params = ','.join(map(lambda x: str(round(x,4)),params))
    string = 'http://api.openstreetmap.org/api/0.6/map?bbox={0}'.format(params)
    #req = requests.get(url,params={'bbox':params})
    req = requests.get(string)
    if verbose:
        print(req.url)
    return req.text

def map_streets_dict(xml):
    osm = etree.fromstring(xml.encode('utf-8'))
    mapable = {node.attrib['id']:{key:value for key,value in node.attrib.items() if key in ['lat','lon']}  for node in osm.findall('node')}
    return mapable

def distance_calc(point1,point2):
    """points are tuple of (lat,lon)"""
    lat1,lon1 = np.radians(point1)
    lat2,lon2 = np.radians(point2)
    return float(np.cosh(np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))*6371)

def rolling_distance(df,window,freq=1,func=distance_calc):
    arr = [float('nan') for i in range(window-1)]
    for i in range(window-1,len(df),freq):
        d = func(df[['lat','lon']].iloc[i-freq],df[['lat','lon']].iloc[i])
        arr.append(d)
    return arr

def test():
    xml = osm_xml_download(-88,41)
    mapable = map_streets(xml)
    mapable.plot_ways()
    #plt.show()
    return mapable

if __name__=='__main__':
    test()
