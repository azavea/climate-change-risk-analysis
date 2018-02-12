"""
Module contains functions to clip and mask vector and raster layers
"""

from subprocess import check_output
from osgeo import ogr


def clip_vector_to_boundaries(input_dataset, overlay):
    """
    Clip a national shp to the extent of the study area

    Args:
        input_dataset (str): the national dataset shapefile
        overlay (analysis.Overlay): Overlay object with bbox attribute

    Returns:
        (str) filepath for resulting shp
    """
    output_dataset = input_dataset.replace('/read/', '/write/')
    output_dataset = output_dataset.replace(
        '.shp', '_{}.shp'.format(overlay.id))
    bbox = overlay.study_area['bbox']
    args = [output_dataset, input_dataset, '-clipsrc'] + bbox
    cmd = "ogr2ogr -f 'ESRI Shapefile' {}".format(' '.join(map(str, args)))
    check_output(cmd, shell=True)
    return(output_dataset)


def maskRasterFromSHP(fullTiff, shp, maskedTiff):
    """
    'Clip' or mask a raster using an shp file as input

    Args:
        fullTiff (str): filepath of full tiff
        shp (str): filepath of shapefile bounding input
        maskedTiff (str): filepath of output tiff
    """
    # TODO: account for geojson
    d = ogr.GetDriverByName("ESRI Shapefile").Open(shp)
    env = d.GetLayer()[0].GetGeometryRef().GetEnvelope()
    args = env[0::2] + env[1::2] + (fullTiff, maskedTiff)
    _maskRaster(args)


def maskRasterFromGDF(fullTiff, gdf, maskedTiff):
    """
    'Clip' or mask a raster using an geodataframe object as input

    Args:
        fullTiff (str): filepath of full tiff
        shp (geopandas.GeoDataFrame): geopandas geodataframe object
        maskedTiff (str): filepath of output tiff
    """
    env = list(gdf.bounds.iloc[0])
    args = env + [fullTiff, maskedTiff]
    _maskRaster(args)


def maskRasterFromBbox(fullTiff, bbox, maskedTiff):
    """
    'Clip' or mask a raster using a bounding box to define boundaries

    Args:
        fullTiff (str): filepath of full tiff
        shp ([float]): list of coordinates
        maskedTiff (str): filepath of output tiff
    """
    args = bbox + [fullTiff, maskedTiff]
    _maskRaster(args)


def _maskRaster(args):
    """
    Mask a raster from a set of coordinates
    """
    cmd = "gdalwarp -overwrite -te {}".format(' '.join(map(str, args)))
    check_output(cmd, shell=True)
