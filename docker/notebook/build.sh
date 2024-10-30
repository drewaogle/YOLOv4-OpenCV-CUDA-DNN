#!/bin/bash

base=$(dirname $(realpath ${0}))/../..

rm -rf notebooks
mkdir notebooks
cp "${base}"/*.ipynb notebooks

docker build -t video-clip-notebook .
rm -rf notebooks
