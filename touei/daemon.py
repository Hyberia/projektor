#!/usr/bin/python
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

__author__ ="GAnime"
__contributors__ = "Martin Samson <pyrolian@gmail.com>"

import time, signal, datetime, os
import mkvutils

# Instanciate the logging
import logging
module_logger = logging.getLogger("touei.daemon")

class ToueiDaemon():
    def __init__(self, playlist, player, config, mkv):
        # Instanciate the logger
        self.logger = logging.getLogger("touei.daemon.ToueiDaemon")
        self.logger.info("Creating instance")

        signal.signal (signal.SIGTERM, self._signalHandler)
        signal.signal (signal.SIGHUP, self._signalHandler)
        self._isRunning = True
        self._Playlist = playlist
        self._Player = player
        self._Config = config
        self._MkvUtils = mkv

    def stop(self):
        self.logger.debug("stop() called")
        self._isRunning = False

    def getCurTime(self):
        self.logger.debug("getCurTime() called. Time is: " + datetime.datetime.now().strftime("%H%M"))
        return datetime.datetime.now().strftime("%H%M")

    def run(self):

        curTime = self.getCurTime()
        CurrentVideoSq = {}
        currentVideo = ""
        self.logger.debug("Entering run loop")
        while(self._isRunning):
            self.logger.debug("Loop begin")
            video = self._Playlist.get()
            self.logger.debug("Current Video: " + currentVideo)
            #self.logger.debug("Playlist Video: " + video['file'])
            if not video:
                # Nothing for current time, Play standby video
                self.logger.debug("No video for current block")
                if currentVideo == self._Config.get("video","standby"):
                    # Standby video is playing
                    self.logger.info("Standby video is playing, sleeping")
                else:
                    # Play the standby video
                    currentVideo = self._Config.get("video","standby")
                    self._Player.openFile(self._Config.get("video","standby"))

            elif currentVideo != video['file']:
                # We have a new video to play (apparently)
                self.logger.debug("Current video is different")
                currentVideoSq = video
                currentVideo = video['file']
                # Create the intro file
                introVideo = self._MkvUtils.generate_intro(os.path.split(video['file'])[1])
                self.logger.debug("Intro video is " + introVideo)
                # Send the intro to player
                self._Player.openFile(introVideo)
                # Send the main video to player
                self._Player.openFile(video['file'], True)
                # Send the outro to player
                #self._Player.openFile(self._Config.get("video","outro"))
            else:
                self.logger.debug("Still playing, sleeping")
            self.logger.debug("Loop ending")
            time.sleep(10)

    def _signalHandler(self,signal,frame):
        self._isRunning = False

if __name__ == "__main__":
    d = ToueiDaemon()
    d.run()
