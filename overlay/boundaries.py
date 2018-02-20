"""
This module contains functions to create new boundary polygons
of user-specified geographies
"""

import os
import geopandas as gpd

from overlay import constants


def get_msa_study_area(msa_search,
                       msa_file_name,
                       msa_output_dir=constants.BOUNDARY_OUTPUT_DIR,
                       all_msas=constants.NATL_MSA_SHP):
    """
    Pull out one MSA from a national msa dataset to use as a 
        study area boundary

    Args:
        msa_name (str): search name to use for msas 
        msa_file_name (str): msa output file name without full path
        msa_output_dir (str): output directory for study area shp
        all_msas (str): path to national msa shapefile

    Returns:
        (str): the path to county output file
    """
    msas = gpd.read_file(all_msas)
    one_msa = msas[msas['NAME'].str.contains(msa_search, case=False)]
    msa_output = os.path.join(msa_output_dir, msa_file_name)
    one_msa.to_file(msa_output)
    return msa_output


def get_county_study_area(county_name,
                          state_fips,
                          county_file_name,
                          county_output_dir=constants.BOUNDARY_OUTPUT_DIR,
                          all_counties=constants.NATL_COUNTY_SHP):
    """
    Pull out one county from a national county dataset to use as a 
        study area boundary

    Args:
        county_name (str): search name to use for counties
        state_fips (str): state fips code 
            https://www.mcc.co.mercer.pa.us/dps/state_fips_code_listing.htm
        county_file_name (str): county output file name without full path
        county_output_dir (str): output directory for study area shp
        all_counties (str): path to national county shapefile

    Returns:
        (str): the path to county output file
    """
    ct = gpd.read_file(all_counties)
    # TODO: add leading zero to this fips code
    # TODO: account for queries that return multiple results
    one_county = ct[(ct['NAME'].str.contains(county_name, case=False))
                    & (ct['STATEFP'] == str(state_fips))]
    county_ouptut = os.path.join(county_output_dir, county_file_name)
    one_county.to_file(county_ouptut)
    return county_ouptutaa
