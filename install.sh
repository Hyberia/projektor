#!/bin/sh
# Author:      G-Anime
# Contributor: Mathieu Charron
# Version:     0.1
# Revision     39
#
# Copyright 2008, Author Name, example.org
# Licensed under the Eiffel Forum License 2.


echo "Building libReadToueiConfig"
cd readconfig
make $1
cd ..

echo "Building toueid"
cd toueid
make $1
cd ..

python setup.py $1
