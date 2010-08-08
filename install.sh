#!/bin/bash
# Author:      G-Anime
# Contributor: Mathieu Charron, Jamie Nadeau
# Version:     0.3.2
#
# Copyright 2008, G-Anime, hyberia.org
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
    echo "Installing HYBERIA"
    python setup.py $COMMAND --record uninstall.db

    echo "Copying support files"
    mkdir /usr/share/fonts/hyberia
    cp misc/*.otf /usr/share/fonts/hyberia/

#end of install
;;
'uninstall')
    echo "Uninstalling HYBERIA"
    cat uninstall.db | xargs rm -rf

    echo "Cleaning support files"
    rm -rf /usr/share/fonts/hyberia

#end uninstall
;;
'clean')
    echo "Cleaning touei"
    python setup.py $COMMAND

;;
esac


