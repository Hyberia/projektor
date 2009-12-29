#!/bin/bash
# Author:      G-Anime
# Contributor: Mathieu Charron, Jamie Nadeau
# Version:     0.1
# Revision     39
#
# Copyright 2008, Author Name, example.org
# Licensed under the Eiffel Forum License 2.

# make sure we're running as root
if [ "$UID" != "0" ]; then
	echo "Sorry, must be root. Exiting..."
  	exit
fi


#Get number of arguments
COMMAND='install'


if ["$1" -eq ""]; then
   COMMAND='install'
else
   COMMAND=$1
fi

case "$COMMAND" in
'install')
	echo "Building libReadToueiConfig"
	cd readconfig
	make

	echo "Installing libReadToueiConfig"
	make $COMMAND
	cd ..

	echo "Building toueid"
	cd toueid
	make
	
	echo "Installing toueid"
	make $COMMAND
	cd ..

	echo "Installing touei"
	python setup.py $COMMAND --record uninstall.db
	
#end of install
;;
'uninstall')
	echo "Uninstalling libReadToueiConfig"
	cd readconfig
	make $COMMAND
	cd ..

	echo "Uninstalling toueid"	
	cd toueid
	make $COMMAND
	cd ..
	
	echo "Uninstalling touei"
	cat uninstall.db | xargs rm -rf
#end uninstall
;;
'clean')
	echo "Cleaning libReadToueiConfig"
	cd readconfig
	make $COMMAND
	cd ..

	echo "Cleaning toueid"	
	cd toueid
	make $COMMAND
	cd ..
	
	echo "Cleaning touei"
	python setup.py $COMMAND
;;
esac


