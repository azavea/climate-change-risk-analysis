"""
Contains Overlay and LayerSet classes
"""
import os
import numpy as np

import geopandas as gpd
import geopyspark as gps
from geopyspark.geotrellis.color import ColorMap, get_colors_from_matplotlib
from geopyspark.geotrellis.tms import TMS
from geonotebook.wrappers import TMSRasterData
from shapely.geometry import MultiPoint, MultiPolygon, MultiLineString, shape

from overlay.data import data, mask


class Overlay(object):
    """
    Overlay analysis in GeoNotebook

    Attributes:
        id (string): unique identifier
        study_area (dict): contains geographic extent of analysis
        layersets (dict):
    """

    # TODO: reclass nodata to zero
    # TODO: clip each to polygon

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
        self.study_area['geom'] = list(polygon.geometry)

        # base layerset
        tiled = build_tiled_from_poly(self.study_area['geom'], 0)
        tiled_masked = tiled.mask(self.study_area['geom'])
        self.study_area['base_raster'] = LayerSet(tiled_masked)

    def build_layerset(self, source, name,
                       tiled_layer=None, polygons=None, pixel_value=1, tiff=None,
                       mplib_palette='viridis', n_colors=None, no_data_color=0x382959FF):
        """
        Construct a full layerset from an already constructed tiledlayer

        Args:
            tiff (string): GeoTiff filebath
            name (string): key in layersets dict
            mplib_palette (string): matplotlib color palette
            n_colors (int): number of colors to use in color ramp
        """
        try:
            if source == 'polygon':
                ls = LayerSet(build_tiled_from_poly(polygons, pixel_value))
            elif source == 'tiled':
                ls = LayerSet(tiled_layer)
            elif source == 'tiff':
                ls = LayerSet(build_tiled_from_tiff(tiff))
            ls.construct_map_layer(mplib_palette, n_colors=None,
                                   no_data_color=no_data_color)
        except:
            print('Source must be one of: "polygon", "tiled" or "tiff"')
        self.layersets[name] = ls


class LayerSet(object):
    """
    Contains all necessary layers to map and analyze a raster
        dataset
    """

    def __init__(self, tiled):
        """
        Construct a layerset

        Args:
            tiled (gps.geopyspark.TiledRasterLayer): initial raster layer
        """
        self.tiled = tiled

    def construct_map_layer(self, mplib_palette='viridis', n_colors=None,
                            no_data_color=0x00000000):
        """
        Construct mapping layers from existing layerset with tiled layer

        args:
            mplib_palette (str): label of matplotlib palette
            n_colors (int): number of color breaks to use in color map
            no_data_color: color to use for NoData values
        """
        self.pyramid = self.tiled.pyramid().cache()
        self.histo = self.pyramid.get_histogram()
        if n_colors is None:
            if self.histo.bucket_count() < 100:
                n_colors = self.histo.bucket_count() + 1
            else:
                n_colors = 100
        self.colors = get_colors_from_matplotlib(mplib_palette, n_colors)
        self.color_map = gps.ColorMap.from_histogram(
            self.histo, self.colors, no_data_color=no_data_color)
        self.tms_layer = gps.TMS.build(self.pyramid, self.color_map)
        self.mappable_layer = TMSRasterData(self.tms_layer)


def build_tiled_from_multi_slr(gdb, overlay, ft_range=(1, 6)):
    """
    Build a tiled layer from a series of sea level rise polygons within a 
        geodatabase. Assign pixels based on the lowest sea level rise 
        threshold that will cover it.

    Args:
        gdb (string): gdb file with 
        overlay (analysis.Overlay): the overlay object defining the
            study area. Study area must have already been set
        ft_range ((int, int)): tuple with range of sea level rise values

    Returns:
        geopyspark.geotrellis.TiledRasterLayer
    """
    feet_vals = list(range(ft_range[0], ft_range[1]))

    def slr_layer(gdb, feet):
        layer_name = os.path.basename(gdb).replace(
            'final_dist.gdb', str(feet) + 'ft')
        sea_level = data.read_from_gdb(gdb, layer_name, MultiPolygon)
        rasterize_options = gps.RasterizerOptions(
            includePartial=True, sampleType='PixelIsArea')
        val = feet + 1
        sl = gps.rasterize(geoms=sea_level,
                           crs="EPSG:3857",
                           zoom=12,
                           fill_value=val,
                           cell_type=gps.CellType.FLOAT32,
                           options=rasterize_options,
                           num_partitions=50)
        return sl.reclassify(value_map={val: val}, data_type=int,
                             classification_strategy=gps.geotrellis.constants.ClassificationStrategy.EXACT,
                             replace_nodata_with=1)

    slr_layers = [slr_layer(gdb, f) for f in feet_vals]
    slr_unioned = gps.geotrellis.union(layers=slr_layers)
    slr_aggregated = slr_unioned.aggregate_by_cell(
        operation=gps.geotrellis.constants.Operation.MIN)
    slr_aggregated = slr_aggregated.tile_to_layout(
        layout=overlay.study_area['base_raster'].tiled.layer_metadata)
    slr_with_base = gps.geotrellis.union(
        layers=[slr_aggregated, overlay.study_area['base_raster'].tiled])
    slr_with_base_aggregated = slr_with_base.aggregate_by_cell(
        operation=gps.geotrellis.constants.Operation.MAX)
    return slr_with_base_aggregated.mask(overlay.study_area['geom'])


def build_tiled_from_poly(polygons, pixel_value):
    """
    Build a layerset from polygons

    Args:
        polygons ([shapely.geometry]): list of shapely geometries to rasterize
        pixel_value (int): value to assign to cells of resulting raster
    """
    return data.rasterize_one_val(polygons, pixel_value)


def build_tiled_from_tiff(tiff):
    """
    Build a layerset from a GeoTiff

    Args:
        tiff (string): filepath for geotiff to buil layerset from
    """
    raster = gps.geotiff.get(layer_type='spatial', uri=tiff)
    return raster.tile_to_layout(
        layout=gps.GlobalLayout(),
        target_crs=3857)
