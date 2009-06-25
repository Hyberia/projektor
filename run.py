#!/usr/bin/python
"""Main script for the Touei project. Need the Touei modules"""

__author__ = "Mathieu Charron"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""

# Configuration

# Set this to your configuration file.
CONFIG_FILE = "touei.conf"


###
# No not change anything below this!
###

# Importation!
import logging
import logging.config
import ConfigParser
import time
import os
import sys
import touei


if __name__ == "__main__":
    # Create the configParser instance
    config = ConfigParser.SafeConfigParser(touei.CONFIG_DEFAULT_VALUE)
    print config
    # Check if the config file exists:
    if os.path.exists(CONFIG_FILE):
        print "Loading config"
        config.read(CONFIG_FILE)
    else: print "Cannot load config"

    # Create Logger
    logging.basicConfig(filename=config.get('logs','main_log'), level=config.getint('logs', 'level'))
    touei_logger = logging.getLogger("touei")

    # Create the console logging
    console = logging.StreamHandler()
    logging.getLogger('touei_logger').addHandler(console)
    print config.get('logs','main_log'), config.get('logs', 'level')
    print logging.WARNING
    #Check if it works
    touei_logger.critical("Application run complete")
