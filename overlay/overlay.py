"""
This module contains the `Overlay` object within which the weighted 
    overlay analysis takes place
"""
import os
import geopandas as gpd
import geopyspark as gps
import numpy as np

from subprocess import call
from urllib import request
from zipfile import ZipFile
from geonotebook.wrappers import TMSRasterData

from overlay import layers, constants


class Overlay(object):
    """
    Overlay analysis in GeoNotebook

    Attributes:
        id (string): unique identifier
        study_area (dict): contains geographic extent of analysis
        layersets (dict):
    """

    # TODO: clip each to polygon

    def __init__(self, id, spatial_file):
        """
        Construct overlay object from a study area

        Args:
            spatial_file (string): path to shp or geojson that defines
                the study area
        """
        self.id = id
        self.study_area = {}
        self.set_study_area(spatial_file)

    def set_study_area(self, spatial_file):
        """
        Define study are attributes from an input shopefile or geojson

        Args:
            spatial_file (string): filepath for shapefile of geojson
                that defines the study area
        """
        # read in study area shp
        self.study_area['shapefile'] = spatial_file
        base_gpd = gpd.read_file(spatial_file)
        base_poly = base_gpd.geometry[0]

        # set the geom and bbox in wgs
        self.study_area['geom_wgs'] = [base_poly]
        bbox = list(base_poly.bounds)
        self.study_area['bbox_wgs'] = bbox

        # centroid
        self.study_area['centroid_wgs'] = {
            'x': np.mean(bbox[0::2]),
            'y': np.mean(bbox[1::2])
        }

        # reproject to web mercator
        if not base_gpd.crs == {'init': 'epsg:3857'}:
            base_poly_wm = base_gpd.to_crs({'init': 'epsg:3857'}).geometry[0]

        # set the geom and bbox in wm
        self.study_area['geom_wm'] = [base_poly_wm]
        self.study_area['bbox_wm'] = list(base_poly_wm.bounds)

        # tiled raster
        base_raster = gps.rasterize(
            [base_poly], 4326, 12, 1, gps.CellType.INT8)
        base_tiled = base_raster.tile_to_layout(gps.GlobalLayout(), 3857)
        self.base = base_tiled

    def prep_data(self, flood_hazard_national, sea_level_rise_url, storm_surge_national):
        """
        Prepare input datasets for all layers

        Args:
            flood_hazard_national (string): path to national flood hazard layer
            sea_level_rise_url (string): link to appropriate sea level rise dataset
                from https://coast.noaa.gov/slrdata/
            storm_surge_national (string): link to national storm surge tiff

        Returns:
            (dict) with paths to all input files of overlay layers
        """
        # save paths to input files
        input_data = {}

        def _new_shp_path(national_shp, extension, id):
            subset_shp = national_shp.replace('/read/', '/write/')
            return subset_shp.replace(extension, '_{}'.format(id) + extension)

        # flood hazard
        flood_hazard_study_area = _new_shp_path(
            flood_hazard_national, '.shp', self.id)
        if os.path.isfile(flood_hazard_study_area):
            print('>> Flood hazard dataset already exists for this study area')
            input_data['flood'] = flood_hazard_study_area
        else:
            print('>> Clipping flood hazard dataset to study area extent...')
            flood_national = gpd.read_file(flood_hazard_national)
            flood_study_area = flood_national[
                flood_national.geometry.intersects(self.study_area['geom_wgs'][0])]
            if len(flood_study_area) > 0:
                flood_study_area.to_file(flood_hazard_study_area)
                input_data['flood'] = flood_hazard_study_area
            else:
                print('>> There are no flood hazard zones in this study area')
                input_data['flood'] = None

        # sea level rise
        #   define file and directory names
        if sea_level_rise_url is None:
            print('>> No sea level rise input')
            input_data['sea_level'] = None
        else:
            sea_level_directory = constants.SEA_LEVEL_DIR
            zip_file_name = os.path.basename(
                os.path.normpath(sea_level_rise_url))
            zip_dir_name = zip_file_name.replace('.zip', '')
            zip_path = os.path.join(sea_level_directory, zip_file_name)
            gdb_directory = os.path.join(sea_level_directory, zip_dir_name)
            gdb_file = (zip_dir_name + '.gdb').replace('data', 'final')
            gdb = os.path.join(gdb_directory, gdb_file)
            #   avoid downloading if the file is already there
            if os.path.isdir(gdb):
                print(
                    '>> Sea level rise dataset has already been downloaded for this study area')
            else:
                print('>> Downloading sea level rise dataset...')
                request.urlretrieve(sea_level_rise_url, zip_path)
                print('>> Extracting sea level rise dataset...')
                ZipFile(zip_path).extractall(gdb_directory)
                os.system('rm {}'.format(zip_path))
            input_data['sea_level'] = gdb

        # storm surge
        storm_surge_study_area = _new_shp_path(
            storm_surge_national, '.tif', self.id)
        if os.path.isfile(storm_surge_study_area):
            print(
                '>> Storm surge tiffs have already been created for this study area')
        else:
            args_storm = self.study_area[
                'bbox_wgs'] + [storm_surge_national, storm_surge_study_area]
            cmd_storm = 'gdalwarp -overwrite -te {}'.format(
                ' '.join(map(str, args_storm)))
            print('>> Clipping storm surge raster to study area extent...')
            call(cmd_storm, shell=True)
        input_data['storm_surge'] = storm_surge_study_area

        return input_data

    def build_layers(self, input_data):
        """
        Build all three layers from input files

        Args:
            input_data (dict): dict with input filenames output or prep_data
        """
        self.flood = layers.flood_hazard(self, input_data['flood'])
        self.sea_level_rise = layers.sea_level_rise(
            self, input_data['sea_level'])
        self.storm_surge = layers.storm_surge(self, input_data['storm_surge'])

    def overlay_layers(self):
        """
        Add all three layers together
        """
        l = [self.flood, self.sea_level_rise, self.storm_surge]
        l = list(filter(None.__ne__, l))
        print('>> Combining {} layers'.format(len(l)))
        self.overlay = sum(l) - len(l)


# Additional Functions


def map_layer(geonotebook, tiled_layer, color_map=None, remove_existing=True):
    """
    Add a tiled raster layer to the map in a Geonotebook

    geonotebook (geonotebook.kernel.Geonotebook): Geonotebook to add to
    tiled_layer (TiledRasterLayer): the layer to add to the map
    color_map (color.ColorMap): color map used to map the layer. If none,
        construct a colormap from Matplotlib 'magma', defaults to None
    """
    print('>> Creating pyramid layer...')
    pyramid_layer = tiled_layer.pyramid()
    if color_map is None:
        print('>> Getting layer histogram...')
        color_map = gps.ColorMap.build(pyramid_layer.get_histogram(), 'magma')
    tms = gps.TMS.build(pyramid_layer, color_map)
    if remove_existing:
        remove_map_layers(geonotebook)
    print('>> Adding weighted overlay layer to map...')
    geonotebook.add_layer(TMSRasterData(tms), name="layer")


def remove_map_layers(geonotebook):
    """
    Remove all layers from the geonotebook map

    geonotebook (geonotebook.kernel.Geonotebook): Geonotebook with layers to remove
    """
    print('>> Removing existing layers from map...')
    for l in geonotebook.layers:
        geonotebook.remove_layer(l)


def overlay_analysis(geonotebook,
                     overlay_name,
                     boundary_shp,
                     sea_url,
                     storm=constants.NATL_STORM_SURGE_1,
                     flood=constants.NATL_FLOOD_SHP,
                     color_map=None):
    """
    This function wraps all steps in the overlay analysis pipeline

    Args:
        geonotebook (geonotebook.kernel.Geonotebook): working geonotebook
        overlay_name (str): id for overlay object
        boundary_shp (str): path to shapefile that defines study area
        sea (str): url for sea level rise input dataset 
        storm (str): national storm surge dataset
        flood (str): national flood dataset
        color_map (gps.ColorMap): color map to use in mapping the result. If 
            None, it will construct one using Matplotlib color ramp 'magma'

    Returns:
        (overlay.Overlay): overlay object for the specified layer
    """

    # set up study area in GeoNotebook
    print('Overlay context')
    print('>> Defining study area boundaries...')
    ov = Overlay(overlay_name, boundary_shp)
    print('>> Setting geonotebook view extent...')
    geonotebook.set_center(ov.study_area['centroid_wgs'][
                           'x'], ov.study_area['centroid_wgs']['y'], 9)

    # pre-process data
    print('Data preparation')
    input_data = ov.prep_data(flood, sea_url, storm)

    # build layers
    print('Analysis')
    print('>> Building layers...')
    ov.build_layers(input_data)

    # overlay layers
    print('>> Combining layers...')
    ov.overlay_layers()

    # add weighted overlay to map
    print('Mapping tiled raster layer...')
    map_layer(geonotebook, ov.overlay, color_map)
    return ov
