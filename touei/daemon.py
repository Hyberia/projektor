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

        signal.signal (signal.SIGTERM, self._signalTerm)
        signal.signal (signal.SIGHUP, self._signalTerm)
        signal.signal (signal.SIGCONT, self._signalCont)
        self._isRunning = True
        self._Playlist = playlist
        self._Player = player
        self._Config = config
        self._MkvUtils = mkv
        self._CurrentVideo = self._Config.get("video","recovery")

    def stop(self):
        self.logger.debug("stop() called")
        self._isRunning = False

    def getCurTime(self):
        self.logger.debug("getCurTime() called. Time is: " + datetime.datetime.now().strftime("%H%M"))
        return datetime.datetime.now().strftime("%H%M")

    def run(self):
        self.logger.debug("Entering run loop")
        curTime = self.getCurTime()
        CurrentVideo = {}
        loopCounter = 0
        while(self._isRunning):
            self.logger.info("Entering Loop %s" % (loopCounter,))
            video = self._Playlist.get()
            self.logger.debug("Current Video: " + self._CurrentVideo)
            #self.logger.debug("Playlist Video: " + video['file'])
            if not video:
                # Nothing for current time, Play standby video
                self.logger.debug("No video for current block")
                if self._CurrentVideo == self._Config.get("video","standby"):
                    # Standby video is playing
                    self.logger.info("Standby video is playing, sleeping")
                else:
                    # Play the standby video
                    self.logger.info("Playing standby video")
                    self._CurrentVideo = self._Config.get("video","standby")
                    self._Player.openFile(self._CurrentVideo)

            elif self._CurrentVideo != video['file']:
                # We have a new video to play (apparently)
                self.logger.debug("Current video is different")
                currentVideo = video
                self._CurrentVideo = video['file']
                # Create the intro file
                introVideo = self._MkvUtils.generate_intro(os.path.split(video['file'])[1])
                self.logger.debug("Intro video is " + introVideo)

                # Send the intro to player
                self._Player.openFile(introVideo)
                # Send the video to player
                self._Player.openFile(self._CurrentVideo, True)
                # Send the outro to player
                #self._Player.openFile(self._Config.get("video","outro"))
            else:
                # Nothing to do, video is playing
                # It could also mean we just went through a _signalCont()
                self.logger.debug("Still playing, sleeping")
            self.logger.debug("Loop ending")
            loopCounter = loopCounter + 1
            time.sleep(10)

    def _signalTerm(self,signal,frame):
        """
        Will exit the loop and let the application close.
        """
        self.logger.warn("SIGNTERM signal received, quitting")
        self._isRunning = False

    def _signalCont(self, signal, frame):
        """
        Signal from the TOUEID process telling the loop that mplayer have
        been restart. replaying the current video.
        """
        if signal == 25:
            # we restore the current video
            self.logger.warn("SIGCONT signal received, restoring video")
            # Force play it
            self._Player.openFile(self._CurrentVideo)
        elif signal == 18:
            # We rebuild the playlist database
            self._Playlist.load(self._Config.get("video", "location"))


if __name__ == "__main__":
    print "##### DEBUG ######"
    d = ToueiDaemon()
    d.run()
