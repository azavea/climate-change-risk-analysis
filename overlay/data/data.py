import fiona
from shapely.geometry import MultiPoint, MultiPolygon, MultiLineString, shape
from functools import partial
import pyproj 
from shapely.ops import transform
from urllib import request
from zipfile import ZipFile
from os.path import basename, normpath, join
import os
import geopyspark as gps


def zip_to_dir(url, directory):
	file = join(directory, basename(normpath(url)))
	request.urlretrieve(url, file)
	ZipFile(file).extractall(file.replace('.zip', ''))
	os.system('rm {}'.format(file))


def read_from_gdb(gdb, layer, shapely_type = MultiPolygon):
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
	rasterize_options = gps.RasterizerOptions(
		includePartial=True, sampleType='PixelIsArea')
	raster = gps.rasterize(
		geoms=polygons,
		crs="EPSG:3857",
		zoom=12,
		fill_value=pixel_val,
		cell_type=gps.CellType.FLOAT32,
		options=rasterize_options,
		num_partitions=50)
	return raster


def _reproj_web_mercator(shape, from_crs):
	reproj = partial(pyproj.transform, 
		pyproj.Proj(init=from_crs), 
		pyproj.Proj(init='epsg:3857'))
	return transform(reproj, shape)
