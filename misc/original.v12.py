#!/usr/bin/python
#
#  run.py
#
# Copyright 2008 Mathieu Charron <mathieu.charron@elwillow.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#  @Version: 0.12
#  @Date: 03.12.2008
__version__ = "0.12"
__license__ = "Apache License, Version 2.0"
__author__ = "Mathieu Charron <mathieu.charron@elwillow.net>"

import os, time, ConfigParser, fileinput, random
from subprocess import *

#####
## WARNING
## ALL THE TIME ARE IN DECIMAL FORM
## 8h00 AM IS 800
## 8h00 PM IS 2000

#### CONFIG
# Location of the fifo file
fifoFile = "/tmp/asdf"

#Location of the pid file
mplayer_pid = "/tmp/mplayer_pid"

# Tampon time for the recovery, aka the time it take to the system to fully recover
recoveryDelay = 2

# filler files List
fillerFiles = ["/home/kiosk/filling.mp4"]

# Location of the config file
configLocation = "/home/kiosk/config/"

# Location of the playlist, use generate.py to generate them
playlistFolder = "/home/kiosk/playlist/"

# The first video file that will play
startFile = "/home/kiosk/eclipse_hd_test.mkv"


# DON'T CHANGE
recoveryState = False

##
# Class: PlayerControl
class PlayerControl():
    """Allow a certain abstraction layer for the mplayer control"""
    def __init__(self, f):
        self.controlFile = os.open(f, os.O_WRONLY)
#        status("DEBUG CRAP! FIX IT BEFORE LIVE DEPLOYMENT",1)
        status("PlayerControl.__init__: Opening file " + f)

    def load(self, path):
        """Load a file in the player, then send fullscreen request"""
        status("PlayerControl.load: loading " + path,-1)
        if path.split(".")[1] == "pls":
            status("PlayerControl.load: We received a playlist", -1)
            os.write(self.controlFile, "loadlist %s\n" % path)
        else:
            status("PlayerControl.load: We received a file", -1)
            os.write(self.controlFile, "loadfile %s\n" % path)
        # force fullscreen, just to be sure
        os.write(self.controlFile, "vo_fullscreen 1\n")
        return 0

    def loadSlot(self, path):
        """Load the new playlist for the and set it fullscreen"""
        status("PlayerControl.loadSlot: Loading " + path, -1)
        os.write(self.controlFile, "loadlist %s\n" % path)
        os.write(self.controlFile, "vo_fullscreen 1\n")
        return 0

    def loadFiller(self, paths, force=False):
        """Load filler. they are append and will be longer than
        the remaining time before the next slot"""
        status("PlayerControl.loadFiller: Number of filler: " + str(len(paths)),-1)
        status("PlayerControl.loadFiller: Force filling: " + str(force),-1)
        for path in paths:
            if force:
                os.write(self.controlFile, "loadfile %s\n" % path)
                status("Force load Filling video " + path,-1)
                force = False
            else:
                os.write(self.controlFile, "loadfile %s 1\n" % path)
        return 0


    def seek(self, seekTime):
        """Change to the given time in the video"""
        status("PlayerControl.seek: Wait 2 sec and seek " + str(seekTime) + " in", -1)
        time.sleep(2)
        os.write(self.controlFile, "seek +" + str(seekTime*60) + "\n")
        return 0

    def finish(self):
        """Close the file"""
        os.close(self.controlFile)
        return 0

##
# Class: ControlPlaylist
class PlaylistControl():
    """Build the playlist from a file and give the path, duration for any
    given time"""
    def __init__(self, file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(file)
        status("PlaylistControl.__init__: Opening file " + file)

    def CurrentSlot(self, time):
        """Return the current slot or zero.
        if in a stasis period (in between slot), return 0"""
        decTime = int(round(time/10)*10)

        foundIt = False
        currentSlot = 2400
#        currentSlot = 0
        while not foundIt:
            # Get the slot runtime, if it's zero, the slot does not exist
            status("PlayerControl.CurrentSlot: Trying slot " + str(decTime), -1)
            if int(self.getSlotRuntime(decTime)):
                # we go a slot, check if the current time is within the runtime
                status("PlayerControl.CurrentSlot: Found it!",-1)
                foundIt = True
                if TimeDiff(decTime,time) < self.getSlotRuntime(decTime):
                    # Within the runtime
                    currentSlot = decTime
                    status("PlayerControl.CurrentSlot: within runtime",-1)
                else:
                    # way outbound
                    status("PlayerControl.CurrentSlot: out of runtime",-1)
                    currentSlot = 0
            else:
                # no slot found, check the one before
                decTime = decTime - 10
            if (not currentSlot) or (not decTime):
                # OKay, stop the infinite loop
                foundIt = True
        return currentSlot

    def getVideo(self, time=0):
        """return the video file that was suppose to play for a given time
        RELATIVE TIME (aka 823 return the 800 video/playlist)
        Return a list with 2 element:
        First: video/list
        second: number of minute to seek INTO the file. 0 mean no seek.

        - Process goes as follow:
        1. If the time is within the first file, send the playlist
        2. if the time is within the second file, send the second file
        3. if there is a bigger fuck up, send an empty string.

        in case of 3, the logic is to fill up the remining time with garbage"""
        # Find the relative time
        slotTime = self.CurrentSlot(time)
        timeIn = time - slotTime

        # Is the timeIn still in the first file (or the only file)?
        if (timeIn < int(self.config.get(str(slotTime),"time1"))):
            # We are, send back the playlist and seek in (timeIn minus recoveryDelay)
            status("PlaylistControl.getVideo: First file",-1)
            return [playlistFolder+str(currentDay)+"/"+str(slotTime)+".pls", timeIn-recoveryDelay]
        else:
            # There is more than one file and we are in the second one
            # should we seek or not?
            if (timeIn - int(self.config.get(str(slotTime),"time1"))) < recoveryDelay:
                # We'll not seek, it's not worth it and it is probably safer
                status("PlaylistControl.getVideo: Second file, within the recoveryDelay; restart. ",-1)
                return [self.config.get(str(slotTime), "file2"), 0]
            else:
                # we'll see the timeIn - recoveryDelay
                status("PlaylistControl.getVideo: Second file, after recoverDelay; seeking",-1)
                return [self.config.get(str(slotTime), "file2"), \
                        timeIn - recoveryDelay - int(self.config.get(str(slotTime), "time1"))]

    def getSlotRuntime(self, time=0):
        """Return the runtime for a give slot, in minutes"""
        x = 0
        try:
            for i in range(1,int(self.config.get(str(time),"count"))+1):
                x = x + int(self.config.get(str(time),"time%s" % (i)))
            status("PlaylistControl.getSlotRuntime: Runtime is " + str(x),-1)
            return x
        except ConfigParser.NoSectionError:
            # The section doesn't exist, return 0
            return 0


##
# Logic
def PlayerStillAlive():
    """Check if the player is still running.
    Return True if not, else False"""
    try:
        status("PlayerStillAlive: Mplayer PID: " + open("/tmp/mplayer_pid").read(), -1)
        return os.path.exists("/proc/%s" % (open("/tmp/mplayer_pid").read()))
    except OSError:
        return False

def TimeDiff(time1, time2):
    """Return the difference between 2 DECIMAL TIME"""

    if time1 < 60: time1 = "00" + str(time1)
    elif time1 < 1000: time1 = "0" + str(time1)
    if time2 < 60: time2 = "00" + str(time2)
    elif time2 < 1000: time2 = "0" + str(time1)

    a = time.strptime("03/06/05 " + str(time1), "%m/%d/%y %H%M")
    b = time.strptime("03/06/05 " + str(time2), "%m/%d/%y %H%M")
    status("TimeDiff: " + str(time2) + " - " + str(time1) + " = " + str(int((time.mktime(b) - time.mktime(a)) / 60)),-1)
    return int((time.mktime(b) - time.mktime(a)) / 60)

def TimeAdd(time1, time2):
    """Return the time1 with the number of minute in time2 added to it"""

    # In case it's before 1000 am.
    if time1 < 60: time1 = "00" + str(time1)
    elif time1 < 1000: time1 = "0" + str(time1)

    a = time.strptime("03/06/05 " + str(time1), "%m/%d/%y %H%M")
    b = time.mktime(a)
    x = time.strftime("%H%M", time.localtime(b + int(time2) * 60))

    status("TimeAdd: " + str(time1) + " + " + str(time1) + " = " + str(x),-1)
    return int(x)

##
# Debug function for now, I might think about create a class of my own
def status(msg, state=0):
    """Format the message to the console to something more readable"""
    if state == -1:
        print "[INFO]", msg
    if state == 0:
        print "[ OK ]", msg
    if state == 1:
        print "[FAIL]", msg
##
# Main loop
if __name__ == "__main__":
    """Main"""
    status("MAIN: application start")
    # Get the current time
    currentTime = time.strftime("%H%M")
    decimalTime = int(currentTime)
    currentDay = time.strftime("%w")
    status("MAIN: Current time is " + currentTime, -1)
    status("MAIN: Current decimal time is " + str(decimalTime), -1)
    status("MAIN: Current day: " + str(currentDay), -1)
    # Default check (file etc..)
    # Do we have the fifo file?
    if not os.path.exists(fifoFile):
        # fifofile is missing, creating a new one
        status("MAIN: Fifo file was absent, recreating",1)
        os.mkfifo(fifoFile)

    # is the pid fil present?
    if not os.path.exists(mplayer_pid):
        # Pid file is missing, touch it
        status("MAIN: Pid file missing, recreating it",1)
        f = open(mplayer_pid,"w")
        f.write("0")
        f.close()

    # If MPlayer is death, assume we have crashed and try to restart the
    # current video to the best of the script (quite bad right now)
    # Check if MPlayer is still running
    if not PlayerStillAlive():
        status("MAIN: Player was dead, starting new one",1)
        # restart the player
        # The command is:
        # xterm -display :0 -e mplayer -slave -fs -input file=/tmp/asdf [FILE]
        p = Popen("/usr/bin/xterm -display :0 -e /usr/bin/mplayer  -slave -input file=%s %s" % (fifoFile, startFile), shell=True)

        # Write the pid
        open(mplayer_pid,"w").write(str(p.pid))

        # Set recovery mode ON!
        recoveryState = True

        # Add a delay, to stablise the player.
        time.sleep(5)
    else:
        status("MAIN: Player is live")

    # Playlist Control
    fileDB = PlaylistControl(configLocation+str(currentDay)+".ini")
    status("MAIN: PlaylistControl created")

    # MPlayer control
    control = PlayerControl(fifoFile)
    status("MAIN: PlayerControl created")

    # Are we in recovery mode?
    if recoveryState:
        status("Recovery Mode: START", 1)
        # okay, we crashed.. time to get the video we had before the blackout
        # back on screen
        # First, what is the time slot?
        crashedSlot = fileDB.CurrentSlot(decimalTime)
        status("Recovery Mode: Crashed slot is: " + str(crashedSlot), -1)

        #Now, what is the running time?
        crashedRuntime = fileDB.getSlotRuntime(crashedSlot)
        status("Recovery Mode: Crashed slot runtime: " + str(crashedRuntime), -1)

        # In the runtime is different than 0 we do have a timeslot
        if crashedRuntime:
            status("Recovery Mode: Preparing recovery",-1)
            # Is it worth to restart? or we can just fill the time until the next slot?
            crashedRemaining = TimeDiff(decimalTime,TimeAdd(crashedSlot,crashedRuntime))
            status("Recovery Mode: crashedRemaining is " + str(crashedRemaining), -1)

            # If the crashedRemining is more than the recoveryDelay AND less
            # than the runtime restart the last video.
            if (crashedRemaining > recoveryDelay) and (crashedRemaining <= crashedRuntime):
                status("Recovery Mode: Entering Video recovery")
                req = fileDB.getVideo(decimalTime)
                status("Recovery Mode: Last played video "+ str(req), -1)
                control.load(req[0])
                if req[1] > 1:
                    status("Seeking " + str(req[1]) + " into the video")
                    control.seek(req[1])
            else:
                status("Recovery Mode: Filling the remaning time")
                control.loadFiller(fillerFiles)
        else:
            # No slot, we'll fill with some filler:
            status("Recovery Mode: Slot is non-existant, sending filler",-1)
            control.loadFiller(fillerFiles, True)
            status("Recovery Mode: Filler send!")
    else:
        # Nope, do normal check:
        status("Entering Normal mode")

        # What is the current slot?
        currentSlot = fileDB.CurrentSlot(decimalTime)
        status("Normal: Current playing slot is "+ str(currentSlot))
        status("If it is zero, we are out of the runtime for the previous slot")
        # Is this a new slot?
        if decimalTime == currentSlot:
            # The previous slot is done, load the new one.
            status("Normal: New time slot")

            # We do.. Get the new slot playlist
            newSlotList = playlistFolder+str(currentDay)+"/"+str(currentSlot)+".pls"
            status("Normal: Playlist is: " + newSlotList)

            #start the new slot
            control.loadSlot(newSlotList)

            status("Normal: Playlist sent!")
            # send a couple of filer after the slot playlist
            control.loadFiller(fillerFiles)

        else:
            # nothing new under the sun...
            status("Normal: No new slot to play")

    # Initiate de closing process
    control.finish()

    status("MAIN: Finish!")

# EOF
