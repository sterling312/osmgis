#!/usr/bin/env python
import osmapi
import numpy as np
import scipy as sp
from scipy import interpolate
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt

class LocationContext(object):
    _nodes = pd.DataFrame() 
    _ways = pd.DataFrame()
    _relations = pd.DataFrame()
    """>>> context = LocationContext.construct_with_center(-87.6231,418769,0.005)"""

    def __init__(self,min_lon,min_lat,max_lon,max_lat,aggr=False):
        """note that longitude corresponds to x-axis and latitude corresponds to y-axis"""
        self.aggr = aggr
        self.api = osmapi.OsmApi()
        self.set_box(min_lon,min_lat,max_lon,max_lat)

    @classmethod
    def construct_with_center(cls,lon,lat,r=0.05,**kwargs):
        """construct class with center node and radius"""
        return cls(lon-r,lat-r,lon+r,lat+r,**kwargs)

    def set_box(self,min_lon,min_lat,max_lon,max_lat):
        """set the frame box for the context"""
        self.box = pd.Series(dict(min_lon=min_lon,
                               min_lat=min_lat,
                               max_lon=max_lon,
                               max_lat=max_lat),name=(min_lon,min_lat,max_lon,max_lat))

    def request_map(self):
        try:
            array = self.api.Map(*self.box.name)
            print('success')
        except osmapi.ApiError as e:
            raise osmapi.ApiError(e.status,e.reason+'-> most likely due to box too big',e.payload)
        # osm data is separted into nodes, ways, and relations. for more info. see openstreetmap.org
        nodes = [i['data'] for i in array if i['type'] == 'node']
        nodes = pd.DataFrame(nodes)
        if len(nodes):
            nodes.index = nodes.id
        ways = [i['data'] for i in array if i['type'] == 'way']
        ways = pd.DataFrame(ways)
        if len(ways):
            ways.index = ways.id
        relations = [i['data'] for i in array if i['type'] == 'relation']
        relations = pd.DataFrame(relations)
        if len(relations):
            relations.index = relations.id
        if self.aggr:
            self._nodes.append(nodes)
            self._ways.append(ways)
            self.relations.append(relations)
        self.nodes = nodes
        self.ways = ways
        self.relations = relations

    def interpolate_ways(self):
        """sets the cubic spline interpolation knots"""
        knot = []
        x = []
        y = []
        for nds in self.ways.nd:
            nodes = self.nodes.loc[nds][['lon','lat']]
            k = 3 if len(nodes)>3 else len(nodes)-1
            k,u = self._interpolate(nodes,k=k)
            _x,_y = self.evaluate_ways(nodes,k)
            knot.append(k)
            x.append(_x)
            y.append(_y)
        self.ways['knot'] = knot
        self.ways['x'] = x
        self.ways['y'] = y

    def _interpolate(self,df,k=3):
        """longitude is x, latitude is y"""
        return interpolate.splprep([df.lon,df.lat],s=0,k=k)
        
    def evaluate_ways(self,nodes,k):
        x,y = interpolate.splev(nodes.lon,k)
        return np.array(x),np.array(y)

    def evaluate_point(self,independent):
        x = []
        y = []
        for k in self.ways.knot:
            _x,_y = map(float,interpolate.splev(independent,k))
            x.append(_x)
            y.append(_y)
        return np.array(x),np.array(y)

