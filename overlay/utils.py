"""
Utility functions for GeoNotebook
"""

import geopyspark as gps

from pyspark import SparkContext


def overlay_geopyspark_conf(appName='ClimateOverlay', memory='12G'):
    conf = gps.geopyspark_conf(appName="ClimateOverlay")
    conf.set('spark.master.memory', '12G')
    conf.set('spark.ui.enabled', True)
    sc = SparkContext(conf=conf)
