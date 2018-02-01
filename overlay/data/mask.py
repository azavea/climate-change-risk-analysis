from osgeo import ogr
from subprocess import check_output

def maskRasterFromSHP(fullTiff, shp, maskedTiff):
    # TODO: account for geojson
    d = ogr.GetDriverByName("ESRI Shapefile").Open(shp)
    env = d.GetLayer()[0].GetGeometryRef().GetEnvelope()
    args = env[0::2] + env[1::2] + (fullTiff, maskedTiff)
    _maskRaster(args)

def maskRasterFromGDF(fullTiff, gdf, maskedTiff):
    env = list(gdf.bounds.iloc[0])
    args = env + [fullTiff, maskedTiff]
    _maskRaster(args)


def maskRasterFromBbox(fullTiff, bbox, maskedTiff):
    args = bbox + [fullTiff, maskedTiff]
    _maskRaster(args)

def _maskRaster(args):
    # TODO: remove file if it's already there
    # check_output("rm -f " + maskedTiff)
    cmd = "gdalwarp -te {}".format(' '.join(map(str,args)))
    check_output(cmd, shell = True)


