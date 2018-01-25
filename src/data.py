import fiona
from shapely.geometry import MultiPoint, MultiPolygon, shape
from functools import partial
import pyproj
from shapely.ops import transform


def read_point_shp(shp):
    '''Read point shapefile'''
    return MultiPoint([shape(f['geometry']) for f in fiona.open(shp)])


def read_polygon_shp(shp):
    '''Read polygon shapefile'''
    return MultiPolygon([shape(f['geometry']) for f in fiona.open(shp)])
