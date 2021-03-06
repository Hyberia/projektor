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
Provide an abstraction layer to control mplayer via the slave command.
"""
__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.4"
__contributors__= "Mathieu Charron, Martin Samson"

import sys,os

# Instanciate the logging
import logging

class SocketLocationException(Exception): pass
class SocketException(Exception): pass
class CommandEmptyException(Exception): pass
class CommandMalformedException(Exception): pass

class PlayerInterface():
    """Abstraction class to Mplayer
    """

    def __init__(self, socketLocation):
        """@param string socketLocation The location of the communication socket
        """

        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.player")
        self.logger.info("Creating instance")

        if not socketLocation:
            raise SocketLocationException()

        if not os.path.exists(socketLocation):
            raise SocketLocationException()

        self.socketLocation = socketLocation
        self.socket = None


        # open socket
        self.openSocket()

        self._commands = {}
        self._commands['open_file'] = "loadfile %s %d\n"
        self._commands['open_playlist'] = "loadlist %s\n"
        self._commands['fullscreen'] = "vo_fullscreen %d\n"
        self._commands['seek'] = "seek %c%d\n"
        self._commands['pause'] = "pause\n"
        self._commands['stop'] = "stop\n"

    def __del__(self):
        if not self.socket:
            return False

        # Close the socket
        self.closeSocket()

    def closeSocket(self):
        """Close the socket. Don't use it lightly.
        """
        self.logger.info("Closing socket")
        try:
            os.close(self.socket)
        except Exception,e:
            print e
            return False
        return True

    def openSocket(self):
        """Open the socket. Don't use it lightly.
        """
        # Will lock until mplayer is listening.
        self.logger.info("Opening socket")
        try:
           self.socket = os.open(self.socketLocation, os.O_WRONLY)
        except Exception,e:
            raise e

    def _communicate(self,command):
        """Communicate with mplayer thru the socket. Does some basic command verifications
        @param string command A command to mplayer.
        @return boolean True/False
        """
        if not self.socket:
            raise SocketException()

        if not command:
            raise CommandEmptyException()

        if not command.endswith("\n"):
            raise CommandMalformedException()

        try:
            os.write(self.socket, command)
        except Exception,e:
            raise e

        return True

    def _execute(self,command):
        """Execute a given command with exception catching
        @param string command The command to execute
        @return boolean True/False
        """
        try:
            result = self._communicate(command)
        except Exception,e:
            self.logger.warn(e)
            return False
        return result
    def pause(self):
        """Pause/Unpause (depending on player status)
        """
        return self._execute(self._commands['pause'])

    def stop(self):
        """Stop the playback.
        """
        return self._execute(self._commands['stop'])

    def fullscreen(self, enabled):
        """Turn on/off fullscreeen
        @param boolean enabled True/False
        @return boolean True/False
        """
        command = None
        if enabled:
            command = self._commands['fullscreen'] % True
        else:
            command = self._commands['fullscreen'] % False

        return self._execute(command)

    def openFile(self, fileLocation, append=False):
        """Open a file
        @param string fileLocation The location of the file
        @param boolean append Append to the current mplayer playlist (True) or play the file (False)
        @return boolean
        """
        command = None
        if fileLocation.endswith('.pls'):
            #We got a playlist
            command = self._commands['open_playlist'] % fileLocation
        else:
            command = self._commands['open_file'] % (fileLocation, append)
        if self._execute(command):
            # Force fullscreen
            self.fullscreen(True)
            self.logger.debug("Command successfully sent: %s" % command.rstrip())
            return True
        else:
            return False

    def seek(self, forward, seekTime):
        """@param boolean forward Going forward(True) or backward(False)
        @param integer seekTime Seek by how many seconds
        @return boolean True/False
        """
        if forward:
            direction = "+"
        else:
            direction = "-"
        if seekTime > 1:
            self.logger.debug("Seeking %s %d seconds" % (direction, seekTime))
            command = self._commands['seek'] % (direction, seekTime)
            return self._execute(command)
        
        return True
