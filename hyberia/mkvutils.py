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
this is the mkvutils module part of the HYBERIA project.
This module do some sanity check before muxing the mkv. It also
control the creation of the subtitle file.
please see http://hyberia.org for more info.
"""

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.4"
__contributors__= "Mathieu Charron, Martin Samson"

# Editing the following will affect all ASS file generated within this
# script.
ASS_HEADER = """[Script Info]
; This script was created by HYBERIA %s
; http://hyberia.org
ScriptType: V4.00+
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Trajan Pro,24,&H0084386B,&HFFFFFFFF,&H00FFFFFF,&HFFDDDDE2,-1,0,0,0,100,100,0,0,1,1,0,1,20,25,20,0
Style: texte-fr,Trajan Pro,22,&H0084386B,&HFFFFFFFF,&H00FFFFFF,&HFFDDDDE2,-1,0,0,0,100,100,0,0,1,1,0,1,20,20,100,0
Style: texte-en,Trajan Pro,18,&H0084386B,&HFFFFFFFF,&H00FFFFFF,&HFFDDDDE2,-1,0,0,0,100,100,0,0,1,1,0,1,30,20,100,0

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:10.00,texte-en,,0000,0000,0000,,{\\fad(250,250)}Next Presentation
Dialogue: 0,0:00:01.00,0:00:10.00,texte-fr,,0000,0000,0000,,{\\fad(250,250)}Prochaine Présentation
""" % (__version__)

# String replacement use:
# first: Start time (0:00:00.00)
# Second: End time (0:00:00.00)
# third: The style (check in the header)
# Last: the text itself
ASS_EVENT = "Dialogue: 0,%s,%s,%s,,0000,0000,0000,,{\\fad(250,250)}%s\n"
import subprocess,re, os, logging

class MkvUtils():

    def __init__(self, config = None):
        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.mkvutils")
        self.logger.info("Creating instance")
        
        #HVIB API 1
        self.HVIB_API_VERSION = 1
        
        self._Config = config

    def HVIB_RunningTime(self,filename):
        '''
        HVIB 1.0 RunningTime adapter
        '''
        return self.mkvTime(filename)
        
    def mkvTime(self,fileName):
        """Return the time in second of the specified filename.
        If return is 0, it means it couldn't get a time.
        """
        reg_exp = re.compile("^\|\ \+\ Duration\:\ (\d+)\.(\d+)\S+")
        times = ()

        # Run the command
        try:
            mkvinfo = subprocess.Popen(['mkvinfo', fileName], shell=False, \
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
        except Exception,e:
            print e
            return 0
        # Read each line
        for line in mkvinfo.stdout.readlines():
            m = reg_exp.match(line)
            if m:
                times = m.groups(0);
        # We found some times
        if times:
            if times[1] > 500:
                seconds = int(times[0]) + 1
            else:
                seconds = times[0] + 0
        else:
            # Could not find the time or is not a MKV file
            return 0

        return seconds
    
    def _gen_event(self, timeStart, duration, style, text):
        """Generate a event string for the ASS generation
        @param string time_start When to display, in seconds
        @param string duration for how long, in seconds
        @param string style What style should the text have
        @param string text the text to display
        @return string the generated string.
        """
        # Time work
        sstime = "0:%02i:%02i.00" % (timeStart/60, timeStart%60)
        etime = timeStart + duration
        setime = "0:%02i:%02i.00" % (etime/60, etime%60)
        return ASS_EVENT % (sstime, setime, style, text)

    def _gen_ass(self, presentation):
        """Generate the ASS file for a given presentation
        @param string presentation
        @return boolean True if error, False if okay
        """
        
        assLocation = "%s/intro.ass" % (self._Config.get("video", "tmp-location"))
        dispText = presentation.title()
        try:
            if os.path.exists(assLocation):
                os.unlink(assLocation)
                
            # Open the file
            assFile = open(assLocation, 'w')
            # Write the header
            assFile.write(ASS_HEADER)
            # Create events
            assFile.write(self._gen_event(1,9,'title',dispText))
            # Close the file
            assFile.close()
        except Exception as e:
            self.logger.critical(e)
            return False
        return True

    def _mux_mkv(self, presentation):
        """Will generate the intro for a given presenation
        @param string the presentation
        @return boolean True if error, False if okay
        """
        # Get the filenames
        assFilename = presentation[:len(presentation)-3]+"ass"
        assLocation = "%s/intro.ass" % (self._Config.get("video", "tmp-location"))
        intro_output = "%s/intro.mkv" % (self._Config.get("video", "tmp-location"))
        
        if os.path.exists(intro_output):
            os.unlink(intro_output)
        # Generate the MKV
        muxingOk = subprocess.call(["mkvmerge", "-o", intro_output, assLocation, self._Config.get("video", "intro")], \
                    shell=False, close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,)
        
        if muxingOk:
            # Muxing fail
            return None
        else:
            return intro_output

    def generate_intro(self, presentation):
        """Primary function. Il will all the sanity check before
        creating the ASS and muxing it.
        @param integer btime The time block
        @param string presentation The raw string from the filename
        @return string The path of the intro video
        """
        
        if not self._gen_ass(presentation):
            return None
        return self._mux_mkv(presentation)
        
            
