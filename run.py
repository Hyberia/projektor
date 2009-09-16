#!/usr/bin/python
# Writer: Mathieu
# Date: 10 Juin 2009
#
# Eiffel Forum License, version 2
#
# 1. Permission is hereby granted to use, copy, modify and/or
#    distribute this package, provided that:
#       * copyright notices are retained unchanged,
#       * any distribution of this package, whether modified or not,
#         includes this license text.
# 2. Permission is hereby also granted to distribute binary programs
#    which depend on this package. If the binary program depends on a
#    modified version of this package, you are encouraged to publicly
#    release the modified version of this package.
#
# THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.

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
