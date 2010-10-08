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
this is the deamon module part of the HYBERIA project.
please see http://hyberia.org for more info.
"""

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.4"
__contributors__= "Mathieu Charron, Martin Samson"

import time, signal, datetime, os, sched, logging
import mkvutils


class HyberiaDaemon():
    """This class provide a way to keep the video database in memory and
    a fast way of checking witch video to play.
    """
    def __init__(self, playlist, player, config, mkv):
        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.daemon")

        signal.signal (signal.SIGTERM, self._signalTerm)
        signal.signal (signal.SIGINT, self._signalTerm)

        #Shouldn't sighup raise a "refresh playlist" event or refresh what is currently playing?
        signal.signal (signal.SIGHUP, self._signalTerm)

        self._isRunning = True
        self._Playlist = playlist
        self._Player = player
        self._Config = config
        self._MkvUtils = mkv
        self.__scheduler = sched.scheduler(time.time,time.sleep)

    def stop(self):
        """Stop the loop
        """
        self.logger.debug("stop called")
        self._Player.stop()
        map(self.__scheduler.cancel, self.__scheduler.queue)

    def run(self):
        """Main daemon routine
        """
        self.__scheduler.enter(0,1, self.events, ())
        self.__scheduler.run()

    def play(self,duration,playList, seekTo = 0):
        #TODO: play the playlist!

        #Schedule next event check
        self.logger.info("Scheduling end of block in %s seconds" % duration)
        
        first = True
        for file in playList:
            if first:
                self._Player.openFile(file,False)
                first = False
            else:
                self._Player.openFile(file,True)
        
        if seekTo > 0:
            self._Player.seek(True,seekTo)
            
        self.__scheduler.enter(duration, 1, self.events,())
        return

    def events(self):

        '''if we are not running, try again in 10 seconds'''
        if not self._isRunning:
            self.logger.debug("We are not running. Trying again in 10 seconds")
            self.__scheduler.enter(10,1,self.events, ())
            return

        block = self._Playlist.getCurrentBlock()
        if not block:
            self.logger.info("Nothing to play.")
            self.__scheduler.enter(10,1,self.events, ())
            return

        self.logger.info("Preparing to play block %s" % block['id'])
        curTime = int(time.time())

        #Transfer in seconds and determine if the presentation isa lready in progress (recovery) or will play next.
        if curTime > block['id']:

            #Recovery
            self.logger.info("Block has already started. Preparing to seek to file.")

            curPart = None
            playList = []
            for part in block['parts']:
                if part['playAt'] < curTime:
                    curPart = part
                    continue

                if playList.count == 0:
                    playList.append(curPart['file'])
                playList.append(part['file'])

            if not curPart:
                self.logger.debug("nothing to play.")
                self.__scheduler.enter(10,1,self.events,())
                return

            self.logger.debug("Verifying if playing %s" % repr(curPart))

            blockStopAt = (block['id'] + block['totalRunTime'])
            
            if curTime > blockStopAt:
                self.logger.debug("Current block has ended. No possible recovery")
                self.__scheduler.enter(30,1,self.events,())
                return

            if curTime > curPart['playAt']:
                self.logger.debug("Part should be currently playing.")
                
                playList.insert(0, curPart['file'])
                
                #seek to the time it should be playing and remove 1 minute for recovery
                seekTo = curTime - curPart['playAt'] - 60

                print seekTo
                
                if (seekTo < 0):
                    seekTo = 0
                
                duration = curPart['duration'] - seekTo
                
                self.__scheduler.enter(0,1,self.play,(duration,playList,seekTo))

                return

            #if we fall here... something very weird has happened...
            self.logger.critical("At the end of recovery process with nothing to recover.")
            self.__scheduler.enter(1,1,self.events,())
            return
        
        else:
            #Play next
            timeTillBlock = block['id'] - curTime
            self.logger.debug("Playing block in %s seconds" % timeTillBlock)
            
            playList = []
            for part in block['parts']:
                playList.append(part['file'])
            
            duration = block['totalRunTime']
            seekTo = 0
            
            intro_file = self._MkvUtils.generate_intro(playList[0])
            if intro_file:
                if timeTillBlock > 10:
                    timeTillBlock -= 10
                else:
                    seekTo = 10 - timeTillBlock
                    
                playList.insert(0,intro_file)
                
            self.__scheduler.enter(timeTillBlock,1,self.play,(duration,playList,seekTo))
            return

    def _signalTerm(self,signal,frame):
        """Will exit the loop and let the application close.
        """
        self.logger.warn("SIGNTERM signal received, quitting")
        self._isRunning = False
        map(self.__scheduler.cancel, self.__scheduler.queue)