from osgeo import ogr
from subprocess import check_output

def clip_vector_to_boundaries(storm_surge_dataset, overlay):
    output_dataset = storm_surge_dataset.replace('/read/', '/write/')
    output_dataset = output_dataset.replace('.shp', '_{}.shp'.format(overlay.id))
    bbox = overlay.study_area['bbox']
    args = [output_dataset, storm_surge_dataset, '-clipsrc'] + bbox
    cmd = "ogr2ogr -f 'ESRI Shapefile' {}".format(' '.join(map(str, args)))
    check_output(cmd, shell = True) 
    return(output_dataset)

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
    # check_output("rm -f " + maskedTiff)
    cmd = "gdalwarp -overwrite -te {}".format(' '.join(map(str, args))) 
    check_output(cmd, shell = True)
