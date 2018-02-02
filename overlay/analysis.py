import geopandas as gpd
import numpy as np
import geopyspark as gps

from geopyspark.geotrellis.color import ColorMap, get_colors_from_matplotlib
from geopyspark.geotrellis.tms import TMS
from geonotebook.wrappers import TMSRasterData

from overlay.data import data, mask


class Overlay(object):
    """
    Overlay analysis in GeoNotebook
    Attributes:
        id (string): unique identifier
    """
    def __init__(self, id):
    	self.id = id
    	self.study_area = {}
    	self.layersets = {}
    	

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

    # TODO: combine into one function with *kwargs
    def layerset_from_tiff(self, tiff, name,
    	mplib_palette = 'viridis', n_colors = None):
    	ls = LayerSet()
    	ls.build_from_tiff(tiff)
    	ls.get_map_layer(mplib_palette, n_colors)
    	self.layersets[name] = ls

    def layerset_from_poly(self, polygons, pixel_value, name,
    	mplib_palette = 'viridis', n_colors = None):
    	# add progress bars
    	ls = LayerSet()
    	ls.build_from_poly(polygons, pixel_value)
    	ls.get_map_layer(mplib_palette, n_colors)
    	self.layersets[name] = ls



class LayerSet(object):
	"""

	"""
	def build_from_poly(self, polygons, pixel_value):
		self.tiled = data.rasterize_one_val(polygons, pixel_value)
		self.pyramid = self.tiled.pyramid().cache()


	def build_from_tiff(self, tiff):
		self.raster = gps.geotiff.get(layer_type='spatial', uri=tiff)
		self.tiled = self.raster.tile_to_layout(
			layout=gps.GlobalLayout(), 
    		target_crs=3857)
		self.pyramid = self.tiled.pyramid().cache()

	def get_map_layer(self, mplib_palette = 'viridis', n_colors = None):
		self.histo = self.pyramid.get_histogram()
		if n_colors is None:
			if self.histo.bucket_count() < 100:
				n_colors = self.histo.bucket_count()
			else:
				n_colors = 100
		self.colors = get_colors_from_matplotlib(mplib_palette, n_colors)
		self.color_map = gps.ColorMap.from_histogram(self.histo, self.colors)
		self.tms_layer = gps.TMS.build(self.pyramid, self.color_map)
		self.mappable_layer = TMSRasterData(self.tms_layer)



    	


 
