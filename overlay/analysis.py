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
        study_area (dict): contains geographic extent of analysis
        layersets (dict): 
    """

    def __init__(self, id):
        """
        Construct overlay object

        Args: 
            id (string): identifier
        """
        self.id = id
        self.study_area = {}
        self.layersets = {}

    def set_study_area(self, spatial_file):
        """
        Define study are attributes from an input shopefile or geojson

        Args:
            spatial_file (string): filepath for shapefile of geojson
                that defines the study area
        """
        polygon = gpd.GeoDataFrame.from_file(spatial_file)
        # TODO: account for multipolygons
        bbox = list(polygon.bounds.iloc[0])
        self.study_area['bbox'] = bbox

        self.study_area['centroid'] = {
            'x': np.mean(bbox[0::2]),
            'y': np.mean(bbox[1::2])
        }
        if not polygon.crs == {'init': 'epsg:3857'}:
            polygon = polygon.to_crs({'init': 'epsg:3857'})
        self.study_area['geom'] = polygon.geometry

    # TODO: combine into one function with *kwargs

    def layerset_from_tiff(self, tiff, name,
                           mplib_palette='viridis',
                           n_colors=None):
        """
        Construct a full layerset from a GeoTiff

        Args:
            tiff (string): GeoTiff filebath
            name (string): key in layersets dict
            mplib_palette (string): matplotlib color palette
            n_colors (int): number of colors to use in color ramp
        """
        ls = LayerSet()
        ls.build_from_tiff(tiff)
        ls.construct_map_layer(mplib_palette, n_colors)
        self.layersets[name] = ls

    def layerset_from_poly(self, polygons, pixel_value, name,
                           mplib_palette='viridis', n_colors=None):
        """
        Construct a full layerset from a list of shapely geometries 

        Args:
            polygons ([shapely.geometry]): GeoTiff filebath
            pixel_value (int): value to assign to rasterized polygon
            name (string): key in layersets dict
            mplib_palette (string): matplotlib color palette
            n_colors (int): number of colors to use in color ramp
        """
        # specify a color for cases with one value
        # add progress bars
        ls = LayerSet()
        ls.build_from_poly(polygons, pixel_value)
        ls.construct_map_layer(mplib_palette, n_colors)
        self.layersets[name] = ls

# TODO: reclass nodata to zero
# TODO: clip each to polygon


class LayerSet(object):
    """
    Contains all necessary layers to map and analyze a raster
        dataset
    """

    def build_from_poly(self, polygons, pixel_value):
        """
        Build a layerset from polygons

        Args:
            polygons ([shapely.geometry]): list of shapely geometries to rasterize
            pixel_value (int): value to assign to cells of resulting raster
        """
        self.tiled = data.rasterize_one_val(polygons, pixel_value)

    def build_from_tiff(self, tiff):
        """
        Build a layerset from a GeoTiff

        Args: 
            tiff (string): filepath for geotiff to buil layerset from
        """
        self.raster = gps.geotiff.get(layer_type='spatial', uri=tiff)
        self.tiled = self.raster.tile_to_layout(
            layout=gps.GlobalLayout(),
            target_crs=3857)

    def construct_map_layer(self, mplib_palette='viridis', n_colors=None):
        """
        Construct mapping layers from existing layerset with tiled layer 
        """
        self.pyramid = self.tiled.pyramid().cache()
        self.histo = self.pyramid.get_histogram()
        if n_colors is None:
            if self.histo.bucket_count() < 100:
                n_colors = self.histo.bucket_count() + 1
            else:
                n_colors = 100
        self.colors = get_colors_from_matplotlib(mplib_palette, n_colors)
        self.color_map = gps.ColorMap.from_histogram(self.histo, self.colors)
        self.tms_layer = gps.TMS.build(self.pyramid, self.color_map)
        self.mappable_layer = TMSRasterData(self.tms_layer)
