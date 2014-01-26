import numpy as np
from matplotlib.mlab import PCA

def average_normalized(input_coord,way_coord):
    """input coord should be a list of (x,y) tuple
    this function takes the average difference between each point to the street and """
    way = np.array(way_coord)
    coord = np.array(input_coord)
    arr = []
    for point in coord:
        arr.append((point+(point-way).mean(axis=0)).tolist())
    return arr

def gaussian_normalized(input_coord,way_coord):
    way = np.array(way_coord)
    coord = np.array(input_coord)
    pass

def pca_normalized(input_coord,way_coord):
    way = np.array(way_coord)
    p = PCA(way)
    coord = np.array(input_coord)
    return p.project(coord).tolist()

