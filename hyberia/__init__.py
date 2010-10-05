#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""
HYBERIA Projection System manage & control the video playback for a
projection room at an Anime Convention
"""

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.3.2"
__contributors__= "Mathieu Charron, Martin Samson"

__all__ = ["player", "playlist", "mkvutils", "daemon"]

CONFIG_DEFAULT_VALUE={"playlist": "cfg/playlist.json",
                      "pid": "/var/pid/hyberia.pid",
                      "slave_socket": "/tmp/hyberia_slave.fifo",
                      "main_log": "/tmp/hyberia_main.log",
                      "debug_level": "20",
                      "seek_delay": "2",
                      "recovery_time": "30",
                      "block_duration": "60",
                      "loop_sleep": "10",
                      "location": "/mnt/video",
                      "tmp-location": "/tmp/hyberia",
                      }
