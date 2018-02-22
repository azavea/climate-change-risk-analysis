#!/bin/bash

# create local aws directory
mkdir -p $HOME/.aws

chmod o+w *.ipynb
chmod o+w data/write/*
chmod o+w data/output

# run container
docker run -it --rm --name geopyspark \
	-p 8000:8000 -p 4040:4040 \
	-v $(pwd $1):/home/hadoop/notebooks:rw \
	-v $HOME/.aws:/home/hadoop/.aws:ro \
	quay.io/geodocker/jupyter-geopyspark:6fe3aa0

