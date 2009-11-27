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

import time,signal, datetime
class ToueiDaemon():
    def __init__(self, playlist, player):
        signal.signal (signal.SIGTERM, self._signalHandler)
        signal.signal (signal.SIGHUP, self._signalHandler)
        self._isRunning = True
        self._Playlist = playlist
        self._Player = player

    def stop(self):
        self._isRunning = False

    def getCurTime(self):
        return datetime.datetime.now().strftime("%H%M")

    def run(self):
        curTime = self.getCurTime()
        currentVideo = {}
        while(self._isRunning):
            video = self._PlayList.get()
            if currentVideo['file'] != video['file']:
                currentVideo = video
                self._Player.play(video)
            time.sleep(10)

    def _signalHandler(self,signal,frame):
        self._isRunning = False

if __name__ == "__main__":
    d = ToueiDaemon()
    d.run()
