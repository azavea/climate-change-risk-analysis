# Introducton

This repository contains the necessary code to perform a weighted overlay analysis to determine areas that are at the greatest risk of being affected by climate change.

The analysis uses [GeoPyspark](https://github.com/locationtech-labs/geopyspark) for raster processing of several geospatial datasets. GeoPySpark provides python bindings to the high-performance data-processing tools in [GeoTrellis](https://geotrellis.io/).

This repository enables you to use GeoPySpark in an [pre-built Docker Container](https://github.com/geodocker/geodocker-jupyter-geopyspark) to create an interactive [GeoNotebook](https://github.com/OpenGeoscience/geonotebook).

# Usage

Note: 'project directory' refers to the top level of this repository.

## Requirements

* Docker

## Getting started

Ensure that project directory has write access:

`chmod o+w [project directory]`

## Open Docker container

Open the Docker container mounting project folder. This will allow you to read from and write to files within this directory from the Docker container.

`./container.sh [project directory]`

Or if you have already navigated to the project directory:

`/container.sh`

The first time that you do this, you will need to download the container image from [quay.io/geodocker/jupyter-geopyspark](https://quay.io/repository/geodocker/jupyter-geopyspark?tag=latest&tab=tags). It will take a few minutes.

After the image has downloaded, it will create a Jupyter server pointed at your local machine. Your default web browser will open and at `localhost:8000`. Refresh your browser. You will be prompted for a username and password, both of which are `hadoop`. After entering these, you will see the project directory in a Jupyter server. Navigate to the Jupyter Notebook of your choice.
