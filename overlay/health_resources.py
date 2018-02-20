"""
This module contains functions to work with health resource point data
"""

import os
import geopandas as gpd
import numpy as np
import pandas as pd

from overlay import overlay, constants


def reproject_wgs(file, directory):
    gdf = gpd.read_file(os.path.join(directory, file))
    gdf_wgs = gdf.to_crs({'init': 'epsg:4326'})
    file_out = file.replace('.shp', '_wgs.shp')
    gdf_wgs.to_file(os.path.join(directory, file_out))


def add_points(geonotebook, shp, colors=[0xFFFFFFFF], name='health'):
    M.add_layer(VectorData(shp), name, colors)


def get_health_point_values(health_points, overlay, output_file):
	"""
	Get raster values at the locations of specified health resources. Subset
		a point file to the study area, add raster values as a attribute and
		write it out as both a shapefile and a csv.

	Args:

	"""

    health = gpd.read_file(health_points)
    health_study_area = health[health.within(overlay.study_area['geom_wm'][0])]
    pt_vals = overlay.overlay.get_point_values(
        list(health_study_area.geometry))
    values = list(map(lambda x: 0.0 if np.isnan(
        x[1][0]) else x[1][0], pt_vals))
    health_study_area['risk_score'] = pd.Series(values)
    health_study_area.to_file(output_file)

    output_csv = output_file.replace('.shp', '.csv')
    hsa_df = pd.DataFrame(health_study_area)
    hsa_df.to_csv(output_csv, index = False)
