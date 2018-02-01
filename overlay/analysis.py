import geopandas as gpd
import numpy as np
import geopyspark as gps

from overlay.data import data, mask


class Overlay(object):
    """
    Overlay analysis in GeoNotebook
    Attributes:
        id (string): unique identifier
    """
    def __init__(self, id):
    	self.id = id
    	self.layers = {}
    	self.study_area = {}

    def set_study_area(self, spatial_file):
    	polygon = gpd.GeoDataFrame.from_file(spatial_file)
    	if not polygon.crs == {'init':'epsg:3857'}:
    		polygon.to_crs({'init':'epsg:3857'})
    	self.study_area['geom'] = polygon.geometry

    	# TODO: account for multipolygons
    	bbox = list(polygon.bounds.iloc[0])
    	self.study_area['bbox'] = bbox

    	self.study_area['centroid'] = {
    		'x': np.mean(bbox[0::2]),
    		'y': np.mean(bbox[1::2])
    		}

    def get_pyramid(tiff):
    	rast = gps.geotiff.get(layer_type='spatial', uri=tiff)
    	rast_tiled = rast.tile_to_layout(
    		layout=gps.GlobalLayout(), 
    		target_crs=3857)
    	rast_pyramided = rast_tiled.pyramid().cache()
    	return rast_pyramided


class LayerSet(object):
	"""

	"""
	def __init__(type):
		self.type = type 


    	


 
