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

"""
this is the PlayerCtrl module part of the Touei project.
please see http://elwillow.net/touei for more info.
"""

__author__ = "Mathieu Charron"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""

class PlayerCtrl():
    """Allow a certain abstraction layer for the mplayer control"""

    def __init__(self, f):
        """Open the control file for the slave control
        WARNING: THE PLAYER MUST RUN BEFORE OPENING THE FILE or the
        command won't go through."""

        self.controlFile = os.open(f, os.O_WRONLY)
        #status("DEBUG CRAP! FIX IT BEFORE LIVE DEPLOYMENT",1)
        #status("PlayerControl.__init__: Opening file " + f)

    def load(self, path):
        """Load a file in the player, then send fullscreen request"""

        #status("PlayerControl.load: loading " + path,-1)
        # Check if we receive a playlist
        if path.split(".")[1] == "pls":
            #status("PlayerControl.load: We received a playlist", -1)
            os.write(self.controlFile, "loadlist %s\n" % path)
        else:
            #status("PlayerControl.load: We received a file", -1)
            os.write(self.controlFile, "loadfile %s\n" % path)

        # force fullscreen, just to be sure
        # @TODO: Shouldn't be needed. I'm sure there is a more elegant
        #        way of doing this -elwillow
        os.write(self.controlFile, "vo_fullscreen 1\n")
        return 0

    def loadFiller(self, paths, force=False):
        """Load filler. they are append and will be longer than
        the remaining time before the next slot. If force=True well,
        force the first file to play."""

        #status("PlayerControl.loadFiller: Number of filler: " + str(len(paths)),-1)
        #status("PlayerControl.loadFiller: Force filling: " + str(force),-1)
        for path in paths:
            if force:
                # Force play
                os.write(self.controlFile, "loadfile %s\n" % path)
                #status("Force load Filling video " + path,-1)
                force = False
            else:
                os.write(self.controlFile, "loadfile %s 1\n" % path)
        return 0

    def seek(self, seekTime):
        """Seek into the video by seekTime minute. Converted to second
        when send to the player."""

        #status("PlayerControl.seek: Wait 2 sec and seek " + str(seekTime) + " in", -1)
        time.sleep(2)
        os.write(self.controlFile, "seek +" + str(seekTime*60) + "\n")
        return 0

    def shutdown(self):
        """Close the control file. Should be call at the end."""
        os.close(self.controlFile)
        return 0
