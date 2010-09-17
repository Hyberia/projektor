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
__version__ = "0.3.2"
__contributors__= "Mathieu Charron, Martin Samson"

import time, signal, datetime, os, sched
import mkvutils

# Instanciate the logging
import logging
logger = logging.getLogger("hyberia.daemon")

class HyberiaDaemon():
    """This class provide a way to keep the video database in memory and
    a fast way of checking witch video to play.
    """
    def __init__(self, playlist, player, config, mkv):
        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.daemon")
        self.logger.info("Creating instance")

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
        self.logger.debug("stop() called")
        self._isRunning = False

    def playerRunning(self):
        """Will check for the player state file deleted by toueid.
        """
        return os.path.exists(self._Config.get("core","tmp-location")+"/player_running")

    def setPlayerRunning(self):
        """Create the file for toueid and the player state (if we crash)
        """
        if not self.playerRunning():
            open(self._Config.get("core","tmp-location")+"/player_running", "w").close()

    def secondsDelta(self, blockStart):
        """Return the number of seconds since the begining of the current block
        @param string blockStart
        """
        delta = datetime.datetime.now() - datetime.datetime.strptime(str(blockStart),"%Y%m%d%H%M")
        print delta
        self.logger.debug("BLOCK DELTA IS %d SECONDS" % (delta.seconds, ) )
        return delta.seconds

    def run(self):
        """Main daemon routine
        """
        self.logger.debug("Entering Run")
        self.__scheduler.enter(0,1, self.events, ())
        self.__scheduler.run()
    
    def play(self,duration,playList):
        #TODO: play the playlist!
        
        #Schedule next event check
        print "scheduling end of block in %s seconds" % duration
        
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
            self.__scheduler.enter(10,1,self.events, ())
            self.logger.debug("nothing to play.")
            #TODO: Get next block and timeout
            return
        
        self.logger.debug("preparing to play block %s" % block['id'])
        curTime = int(time.time())
        
        #Transfer in seconds and determine if the presentation isa lready in progress (recovery) or will play next.
        if curTime > block['id']:
            
            #Recovery
            self.logger.debug("block has already started. preparing to seek to file.")
            
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
            
            self.logger.debug("verifying if playing %s" % repr(curPart))
            
            blockStopAt = (block['id'] + block['totalRunTime'])
            if curTime > blockStopAt:
                self.logger.debug("current block has ended. no possible recovery")
                self.__scheduler.enter(30,1,self.events,())
                return
            
            if curTime > curPart['playAt']:
                self.logger.debug("part should currently be playing.")
                
                seekTo = curTime - curPart['playAt']
                
                duration = curTime - block['id']
                
                #Give 30 sec back to the people?
                if seekTo > 180:
                    seekTo -= 180
                    duration -= 180
                
                #TODO: Send playlist and seek
                self.__scheduler.enter(0,1,self.play,(duration,playList))
                
                return
            
            #if we fall here... something very weird has happened...
            self.logger.critical("got to the end of recovery process with nothing to recover.")
            self.__scheduler.enter(1,1,self.events,())
            return
        else:
            #Play next
            timeTillBlock = block['id'] - curTime
            self.logger.debug("block will start in %s seconds" % timeTillBlock)
            self.__scheduler.enter(timeTillBlock,1,self.play,(block,))
            return
        
        

    def comp_dates(self, d1, d2):
        # Date format: %Y-%m-%d %H:%M:%S
        return time.mktime(time.strptime(d2,"%Y%m%d%H%M%S"))-\
               time.mktime(time.strptime(d1, "%Y%m%d%H%M%S"))


        '''
            
            self.block = self._Playlist.getCurrentBlock()
            self.logger.debug("Current Video: " + self._CurrentVideo)
            self.logger.debug("self.video = " + str(self.video))
            #self.logger.debug("Playlist Video: " + video['file'])
            if self.video == None:
                # Nothing for current time, Play standby video
                self.logger.debug("No video for current block")
                if self._CurrentVideo == self._Config.get("video","standby"):
                    # Standby video is playing
                    self.logger.info("Standby video is playing, sleeping")
                else:
                    # Play the standby video
                    self.logger.info("Playing standby video")
                    self._CurrentVideo = self._Config.get("video","standby")
                    # Open the file is "soft" mode, aka append.
                    self._Player.openFile(self._CurrentVideo, True)

            elif self._CurrentVideo != self.video['file']:
                # We have a new video to play (apparently)
                self.logger.debug("Current video is different")
                currentVideo = self.video
                self._CurrentVideo = self.video['file']
                # Create the intro file
                introVideo = self._MkvUtils.generate_intro(os.path.split(self.video['file'])[1])
                self.logger.debug("Intro video is " + introVideo)

                bDelta = self.secondsDelta(self.video['datetime_start'])

                # Check if the video is alive
                if not self.playerRunning():
                    # Not running, we have to restore the video
                    self.logger.warn("Player was dead, restoring")
                    # Check if we want the intro video
                    if bDelta < self._Config.getint("timing", "loop_sleep") * 2:
                        # Within the sleep timer
                        self.logger.info("Within the loop_sleep time, Playing block")
                        self._Player.openFile(introVideo)
                        self._Player.openFile(self._CurrentVideo, True)

                    # Send the video to player
                    self._Player.openFile(self._CurrentVideo, True)

                    # Check if we need to seek
                    if bDelta > self._Config.getint("timing","recovery_time"):
                        # We need to seek
                        self.logger.info("Over the recovery time, seeking")
                        # Send the seek commands
                        self._Player.seek(True, bDelta)
                    else:
                        # We are within the recovery time, don't seek
                        self.logger.info("Restoring: Wihin the recovery, doing nothing")
                    # Send the intro to player


                    # Send the outro to player
                    #self._Player.openFile(self._Config.get("video","outro"))
                    # Recreate the file
                    self.setPlayerRunning()
                else:
                    # Player is still alive
                    self.logger.warn("Player is still alive.")
                    # Send the video to the player
                    if bDelta < self._Config.getint("timing", "loop_sleep"):
                        # Within the sleep timer
                        self.logger.info("Within the loop_sleep time, Playing block")
                        self._Player.openFile(introVideo)
                        self._Player.openFile(self._CurrentVideo, True)
            else:
                # Nothing to do, video is playing
                # It could also mean we just went through a _signalCont()
                self.logger.debug("Still playing, sleeping")

            # Loop is over
            self.logger.debug("Loop ending")
            time.sleep(self._Config.getint("timing", "loop_sleep") )
        '''
    def _getFormattedDateTime(self, format = "%Y%m%d%H%M"):
        return int(datetime.datetime.now().strftime(format))
        
    def _signalTerm(self,signal,frame):
        """Will exit the loop and let the application close.
        """
        self.logger.warn("SIGNTERM signal received, quitting")
        self._isRunning = False
        if self.playerRunning():
            os.remove(self._Config.get("core","tmp-location")+"/player_running")

if __name__ == "__main__":
    print "##### DEBUG ######"
    
    ch = logging.StreamHandler()
    cformatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
    ch.setFormatter(cformatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
        
    from mkvutils import MkvUtils
    from playlist import PlayList
    m = MkvUtils()
    p = PlayList(m)
    p.load('../cfg/playlist.json')
    
    #(self, playlist, player, config, mkv)
    d = HyberiaDaemon(p,None,None,m)
    d.run()
