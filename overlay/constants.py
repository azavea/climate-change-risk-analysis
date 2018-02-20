
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
HOSPITALS = '/home/hadoop/notebooks/data/read/health/Hospitals_wgs.shp'
