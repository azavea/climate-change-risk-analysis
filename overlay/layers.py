"""
Create three overlay layers
"""

import os
import numpy as np
import geopandas as gpd
import geopyspark as gps
import fiona

from osgeo import ogr
from shapely.geometry import MultiPolygon, shape


def flood_hazard(overlay, flood_shp):
    """
    Create a tiled flood hazard raster
    """
    if flood_shp is None:
        return None
    else:
        # read flood shp
        shapes = gpd.read_file(flood_shp)
        flood_poly = [s for s in shapes.geometry if s is not None]

        # rasterize
        flood_raster = gps.rasterize(
            flood_poly, 4326, 12, 5, gps.CellType.INT8)

        # reclassify values to fit on 1-7 scale
        flood_reclass = flood_raster.reclassify(value_map={5: 5},
                                                data_type=int,
                                                replace_nodata_with=1,
                                                classification_strategy=gps.ClassificationStrategy.EXACT)

        # layout
        flood_tiled = flood_reclass.tile_to_layout(gps.GlobalLayout(), 3857)

        # convert to an appropriate format for the overlay
        return _union_with_base(flood_tiled, overlay)


def sea_level_rise(overlay, gdb, feet=5):
    """
    Create a tiled sea level rise layer
    """
    if gdb is None:
        return None
    else:
        # open geodatabase
        driver = ogr.GetDriverByName("OpenFileGDB")
        g = driver.Open(gdb)

        # find appropriate layer name
        suffix = 'slr_{}ft'.format(str(feet))
        for x in range(g.GetLayerCount()):
            layer_name = g.GetLayerByIndex(x).GetName()
            if layer_name.endswith(suffix):
                break

        # read sea level rise polygons
        sea_poly = []
        with fiona.open(gdb, layer=layer_name) as source:
            slr_crs = source.crs['init']
            for p in source:
                sea_poly += MultiPolygon(shape(p['geometry']))

        # rasterize
        sea_raster = gps.rasterize(sea_poly, 4326, 12, 5, gps.CellType.INT8)

        # reclassify values to fit on 1-7 scale
        sea_reclass = sea_raster.reclassify(value_map={5: 5},
                                            data_type=int,
                                            replace_nodata_with=1,
                                            classification_strategy=gps.ClassificationStrategy.EXACT)

        # convert layout
        sea_tiled = sea_reclass.tile_to_layout(gps.GlobalLayout(), 3857)

        return _union_with_base(sea_tiled, overlay)


def storm_surge(overlay, storm_surge_tiff):
    """
    Create a tiled storm surge layer
    """

    # read in tiff
    storm_raster = gps.geotiff.get(gps.LayerType.SPATIAL,
                                   storm_surge_tiff,
                                   max_tile_size=128,
                                   num_partitions=32)

    # specify value map
    rmap = {}
    i = 2
    for x in range(1, 21, 3):
        rmap[x + 1] = int(i)
        i += 1

    # reclassify storm surge
    storm_reclass = storm_raster.reclassify(value_map=rmap,
                                            data_type=int,
                                            replace_nodata_with=1,
                                            classification_strategy=gps.ClassificationStrategy.GREATER_THAN_OR_EQUAL_TO)

    # convert to same layout as
    storm_tiled = storm_reclass.tile_to_layout(gps.GlobalLayout(), 3857)
    return storm_tiled * overlay.base


def _union_with_base(tiled, overlay, value_map={5: 5, 1: 1}, classification_strategy=gps.ClassificationStrategy.EXACT):
    """
    Helper function ('private') to combine a layer with it's base layer and
            convert no data values to 1
    """
    unioned_base = gps.geotrellis.union(layers=[tiled, overlay.base])
    agg_base = unioned_base.aggregate_by_cell(
        operation=gps.geotrellis.constants.Operation.MAX)
    agg_reclass = agg_base.reclassify(value_map=value_map,
                                      data_type=int,
                                      replace_nodata_with=1,
                                      classification_strategy=classification_strategy)
    return agg_reclass * overlay.base
