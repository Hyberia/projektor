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

"""
this is the mkvutils module part of the Touei project.
This module do some sanity check before muxing the mkv. It also
control the creation of the subtitle file.
please see http://elwillow.net/touei for more info.
"""

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""
__contributors__= "Mathieu Charron, Martin Samson"

# Editing the following will affect all ASS file generated within this
# script.
ASS_HEADER = """[Script Info]
; This script was created by subtitleeditor (0.30.0)
; http://home.gna.org/subtitleeditor/
; Note: This file was saved by Subresync.
; This file was create automaticly by Touei
ScriptType: V4.00+
Timer: 100.0000

Collisions: Normal

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: default,DejaVu Sans,18,&H000000E8,&H00FFFFFF,&H00000000,&H7ADDDDE2,-1,0,0,0,100,100,0,0,1,1,1,2,20,20,20,1
Style: top,DejaVu Sans,18,&H000000E8,&H00FFFFFF,&H00000000,&H7FDDDDE2,-1,0,0,0,100,100,0,0,1,1,1,7,20,20,20,0
[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
"""

# String replacement use:
# first: Start time (0:00:00.00)
# Second: End time (0:00:00.00)
# third: The style (check in the header)
# Last: the text itself
ASS_EVENT = "Dialogue: 0,%s,%s,%s,,0000,0000,0000,,{\\fad(250,250)}%s\n"
import subprocess,re
class MkvUtils():

    def __init__(self):
        pass

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

    def _already_muxed(self, presentation):
        """Check if the presentation was already muxed
        @param string presentation
        @return boolean True/False
        """
        return os.path.exists("%s/intro/%s"% (debug_config_tmp, presentation))

    def _already_assed(self, presentation):
        """Check if the ASS for a given presentation exist
        @param string presentation
        @return boolean True/False
        """
        # Get the filename
        ass_filename = presentation[:len(presentation)-3]+"ass"
        return os.path.exists("%s/ass/%s"% (debug_config_tmp, ass_filename))

    def _gen_ass(self, presentation):
        """Generate the ASS file for a given presentation
        @param string presentation
        @return boolean True if error, False if okay
        """
        # Get the filename
        assFilename = presentation[:len(presentation)-3]+"ass"
        dispText = presentation.split(".")[1].replace("_", " ").title()
        # Open the file
        assFile = open("%s/ass/%s" % (debug_config_tmp, assFilename), 'w')
        # Write the header
        assFile.write(ASS_HEADER)
        # Create events
        assFile.write(self._gen_event(0,6,'top',"Sponsored by Magmic Games"))
        assFile.write(self._gen_event(1,3,'default',"Next Presentation: " + dispText))
        assFile.write(self._gen_event(4,3,'default',"Prochaine Presentation: " + dispText))
        # Close the file
        assFile.close()
        return 0

    def _mux_mkv(self, presentation):
        """Will generate the intro for a given presenation
        @param string the presentation
        @return boolean True if error, False if okay
        """
        # Get the filenames
        assFilename = presentation[:len(presentation)-3]+"ass"
        assLocation = "%s/ass/%s" % (debug_config_tmp, assFilename)
        intro_output = "%s/intro/%s" % (debug_config_tmp, presentation)
        # Generate the MKV
        muxingCmd = subprocess.call(["mkvmerge", "-o", intro_output, assLocation, debug_config_intro], \
                    shell=False, close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,)
        return muxingCmd

    def generate_intro(self, presentation):
        """Primary function. Il will all the sanity check before
        creating the ASS and muxing it.
        @param integer btime The time block
        @param string presentation The raw string from the filename
        @return boolean True if error, False if okay
        """
        # check if the file exist
        if self._already_assed(presentation):
            print "ASS: Present"
            # Do we have a MKV?
            if self._already_muxed(presentation):
                # We do... do nothing
                print "MKV: Present"
                return 0
            else:
                # We'll take the already create ASS for the muxing
                print "MKV: Generating..."
                self._mux_mkv(presentation)
                return 0
        else:
            print "ASS: Missing"
            # Do we have a intro MKV?
            if self._already_muxed(presentation):
                # strange, no ass but there is a MKV for the intro.
                # Won't do a thing
                print "MKV: Present"
                return 0
            else:
                print "MKV: Missing"
                # We have to generate the whole intro file
                print "ASS: Generating..."
                self._gen_ass(presentation)
                print "ASS: Generating..."
                self._mux_mkv(presentation)
                return 0


# Debug
if __name__ == "__main__":
    print "##### DEBUG ######"
    # importation
    import os
    # Temporary config value for debug
    debug_config_tmp = "/tmp/touei"
    debug_config_intro = "/home/elwillow/workspace/Touei/intro.mkv"

    mkv = MkvUtils()
    #print mkv._gen_event(3,2,"Top","TESTING A EVENT LINE!")
    #print os.path.exists(debug_config_intro)

    mkv.generate_intro("1545.Higurashi_no_Naku_Koro_ni.mkv")



# EOF
