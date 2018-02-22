"""
Constant values for overlay abalysis
"""

import geopyspark as gps

# color map values
COLORS = [1023,
          185083135,
          521227263,
          990867455,
          1460960767,
          1897890303,
          2351530239,
          2805038591,
          3275453695,
          3712575743,
          4032847359,
          4202651391,
          4255083775,
          4273898495,
          4259160063,
          4227645439]
VALUES = list(range(0, 16))

# data directory
DATA_DIR = '/home/hadoop/notebooks/data/'

# national storm surge layers for different categories of storm
NATL_STORM_SURGE_1 = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category1_MOM_Inundation_HighTide.tif'
NATL_STORM_SURGE_2 = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category2_MOM_Inundation_HighTide.tif'
NATL_STORM_SURGE_3 = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category4_MOM_Inundation_HighTide.tif'
NATL_STORM_SURGE_4 = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category4_MOM_Inundation_HighTide.tif'
NATL_STORM_SURGE_5 = '/home/hadoop/notebooks/data/read/overlay-layers/storm-surge/US_Category5_MOM_Inundation_HighTide.tif'

# national flood layer
NATL_FLOOD_SHP = '/home/hadoop/notebooks/data/read/overlay-layers/flood/Fld_Haz_ar.shp'

# sea level directory
SEA_LEVEL_DIR = '/home/hadoop/notebooks/data/read/overlay-layers/sea-level-rise/'

# output directory for new boundary shps
BOUNDARY_OUTPUT_DIR = '/home/hadoop/notebooks/data/write/boundaries/'

# boundaries source shps
NATL_MSA_SHP = '/home/hadoop/notebooks/data/read/boundaries/tl_2015_us_cbsa.shp'
NATL_COUNTY_SHP = '/home/hadoop/notebooks/data/read/boundaries/tl_2017_us_county.shp'

# NOAA url base
NOAA_URL_BASE = 'https://coast.noaa.gov/htdata/Inundation/SLR/SLRdata/'

# hospitals
HOSPITALS_WGS = '/home/hadoop/notebooks/data/read/health/Hospitals_wgs.shp'
HOSPITALS_WM = '/home/hadoop/notebooks/data/read/health/Hospitals.shp'

# state fips codes
STATE_FIPS = {
    'AK': '02', 'AL': '01', 'AR': '05', 'AZ': '04', 'CA': '06',
    'CO': '08', 'CT': '09', 'DC': '11', 'DE': '10', 'FL': '12',
    'GA': '13', 'HI': '15', 'IA': '19', 'ID': '16', 'IL': '17',
    'IN': '18', 'KS': '20', 'KY': '21', 'LA': '22', 'MA': '25',
    'MD': '24', 'ME': '23', 'MI': '26', 'MN': '27', 'MO': '29',
    'MS': '28', 'MT': '30', 'NC': '37', 'ND': '38', 'NE': '31',
    'NH': '33', 'NJ': '34', 'NM': '35', 'NV': '32', 'NY': '36',
    'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44',
    'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49',
    'VA': '51', 'VI': '78', 'VT': '50', 'WA': '53', 'WI': '55',
    'WV': '54', 'WY': '56', 'N/A': None
}

# output directory
OUTPUT_DIR = '/home/hadoop/notebooks/data/output/'

# matching name of each health facility type with corresponding shapefile
HEALTH_RESOURCE_FILES = {'Hospitals': '/home/hadoop/notebooks/data/read/health/Hospitals.shp',
                         'Medical centers': '/home/hadoop/notebooks/data/read/health/MedicalCenters.shp',
                         'County healthcare resources': '/home/hadoop/notebooks/data/read/health/County_HealthcareResources.shp',
                         'Federally qualified health centers': '/home/hadoop/notebooks/data/read/health/FederallyQualifiedHealthCenters.shp',
                         'Home health services': '/home/hadoop/notebooks/data/read/health/HomeHealthServices.shp',
                         'State healthcare Resources': '/home/hadoop/notebooks/data/read/health/State_HealthcareResources.shp',
                         'Nursing homes': '/home/hadoop/notebooks/data/read/health/NursingHomes.shp',
                         'Congressional district healthcare resources': '/home/hadoop/notebooks/data/read/health/CongressionalDistrict_HealthcareResources.shp'}
