from osgeo import ogr
from subprocess import check_output

def clipRasterFromSHP(fullTiff, shp, maskedTiff):
    # TODO: account for bounding masks w/ multiple polygons
    # TODO: account for geojson
    # TODO: problems with write access
    d = ogr.GetDriverByName("ESRI Shapefile").Open(shp)
    env = d.GetLayer()[0].GetGeometryRef().GetEnvelope()
    args = env[0::2] + env[1::2] + (fullTiff, maskedTiff)
    cmd = "gdalwarp -te {}".format(' '.join(map(str,args)))
    check_output(cmd, shell = True)

def clipRasterFromGDF(fullTiff, gdf, maskedTiff):
    # TODO: problems with write access
    env = list(gdf.bounds.iloc[0])
    args = env + [fullTiff, maskedTiff]
    # TODO: remove file if it's already there
    # check_output("rm -f " + maskedTiff)
    cmd = "gdalwarp -te {}".format(' '.join(map(str,args)))
    check_output(cmd, shell = True)