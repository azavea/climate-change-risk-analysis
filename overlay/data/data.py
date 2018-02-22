"""
Data import function
"""

import os
from os.path import basename, normpath, join

import fiona
import pyproj
import geopandas as gpd
import geopyspark as gps
from shapely.geometry import MultiPoint, MultiPolygon, MultiLineString, shape
from shapely.ops import transform
from functools import partial
from urllib import request
from zipfile import ZipFile


def zip_to_dir(url, directory):
    """
    Download a zipfile from a url and unzip it into a local directory

    Args:
        url (str): url of zip file
        directory (str): output directory
    """
    file = join(directory, basename(normpath(url)))
    request.urlretrieve(url, file)
    ZipFile(file).extractall(file.replace('.zip', ''))
    os.system('rm {}'.format(file))


def read_from_shp(file):
    """
    Read a shapefile or geojson and return shapely geometries

    Args:
        file (str): input filepath

    Returns:
        list of shapely.geometry objects
    """
    shapes = gpd.read_file(file)
    # this is a temporary hack, was having a difficult time
    # remove NoneType geometries
    shapes = shapes[shapes['SHAPE_Leng'] > 0]
    shapes_wm = shapes.to_crs({'init': 'epsg:3857'})
    return [s for s in shapes_wm.geometry if s is not None]


def read_from_gdb(gdb, layer=0, shapely_type=MultiPolygon):
    """
    Read a layer from a geodatabase and return shapely geometries

    Args:
            file (str): input filepath of gdb
            layer (int): index of geodatabase layer
            shapely_type (func): one of MultiPolygon, MuliPoint, etc.
                    defaults to MultiPolygon

    Returns:
            list of shapely.geometry objects
    """
    with fiona.open(gdb, layer=layer) as source:
        slr_crs = source.crs['init']
        slr = []
        for p in source:
            poly = shapely_type(shape(p['geometry']))
            if slr_crs is not 'epsg:3857':
                poly = _reproj_web_mercator(poly, slr_crs)
            slr += [poly]
    return slr


def rasterize_one_val(polygons, pixel_val):
    """
    Rasterize a set of polygons with one val

    Args:
            polygons ([shapely.polygon]): geometries to rasterize
            pixel_val (int): value to assign to all pixels

    Returns:
            geopyspark.geotrellis.RasterLayer
    """
    rasterize_options = gps.RasterizerOptions(
        includePartial=True, sampleType='PixelIsArea')
    raster = gps.rasterize(
        geoms=polygons,
        crs="EPSG:3857",
        zoom=13,
        fill_value=pixel_val,
        cell_type=gps.CellType.INT32,
        options=rasterize_options,
        num_partitions=50)
    return raster


def _reproj_web_mercator(shape, from_crs):
    """
    Reproject shapely object to web mercator

    Args:
            shape (shapely.geometry): geom to reporoject
            from_crs (dict): initial crs to reproject from

    Returns:
            shapely.geometry
    """
    reproj = partial(pyproj.transform,
                     pyproj.Proj(init=from_crs),
                     pyproj.Proj(init='epsg:3857'))
    return transform(reproj, shape)
