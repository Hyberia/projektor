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

"""Touei is a Projection management controller for projection room at an
   Anime Convention"""

__author__ = "Mathieu Charron"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""

__all__ = ["player", "playlist", "mkvutils", "utils"]

CONFIG_DEFAULT_VALUE={"pid": "/var/pid/touei.pid",
                      "slave_socket": "/tmp/touei_slave.fifo",
                      "deamon_log": "touei_deamon.log",
                      "main_log": "touei_main.log",
                      "level": "30",
                      "seek_delay": "2",
                      "recovery_time": "70",
                      "block_duration": "60",
                      "location": "/home/video",
                      "recovery": "%(location)/recovery.mkv",
                      "standby": "%(location)/standby.mkv",
                      "intro": "%(location)/intro.mkv",
                      "outro": "%(location)/outro.mkv",
                      "countdown": "%(location)/countdown.mkv",
                      }


# Load sub modules
from mkvutils import *
from playlist import *
from player import *

# Load function
from utils import *
