#!/bin/bash

chmod 777 climate-overlay.ipynb
chmod 777 data/write/boundaries/
chmod 777 data/write/overlay-layers/*
chmod 777 data/output/

# create local aws directory
mkdir -p $HOME/.aws

# run container
docker run -it --rm --name geopyspark \
	-p 8000:8000 -p 4040:4040 \
	-v $(pwd $1):/home/hadoop/notebooks:rw \
	-v $HOME/.aws:/home/hadoop/.aws:ro \
	quay.io/geodocker/jupyter-geopyspark:6fe3aa0

