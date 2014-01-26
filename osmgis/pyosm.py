#!/usr/bin/env python
import os
import sys
import subprocess
if sys.version_info.major>2:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen
import numpy as np
import matplotlib.pyplot as plt
from lxml import html

def osm_xml_download(x1,y1,x2=None,y2=None):
    if not x2: 
        x2=x1+0.05
    if not y2: 
        y2=y1+0.05
    string = 'http://api.openstreetmap.org/api/0.6/map?bbox={0:1.4f},{1:1.4f},{2:1.4f},{3:1.4f}'.format(x1,y1,x2,y2)
    xml = urlopen(string).read()
    return xml

def map_streets(xml):
    osm = html.fromstring(xml)
    nodes = osm.findall('node')
    nd_dict = {int(node.attrib['id']):[float(node.attrib.get('lat',np.nan)),float(node.attrib.get('lon',np.nan))] for node in nodes}
    ways = osm.findall('way')
    for way in ways:
        coord = []
        for nd in way.findall('nd'): 
            nd.coord = nd_dict.get(int(nd.attrib['ref']),(np.nan,np.nan))
            coord.append(nd.coord)
        way.coord = coord
    return ways,nodes,nd

def distance_calc(point1,point2):
    """points are tuple of (lat,lon)"""
    lat1,lon1 = np.radian(point1)
    lat2,lon2 = np.radian(point2)
    return float(np.cosh(np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))*6371)

def test():
    xml = osm_xml_download(-88,41)
    ways,nodes,nd = map_streets(xml)
    coord = np.array(ways[0].coord)
    #plt.plot(coord[:,0],coord[:,1])
    #plt.show()
    return coord
