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
this is the mkvutils module part of the Touei project.
This module do some sanity check before muxing the mkv. It also
control the creation of the subtitle file.
please see http://elwillow.net/touei for more info.
"""

__author__ = "Mathieu Charron"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""


class MkvUtils():
    def ping():
        return "Pong!"
        
    def mkvTime(fileName):
        """Return the time in second of the specified filename.
        If return is 0, it means it couldn't get a time."""
        cmd = "mkvinfo " + file_name
        reg_exp = re.compile("^\|\ \+\ Duration\:\ (\d+)\.(\d+)\S+")
        times = ()
    
        # Run the command
        mkvinfo = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, \
                                                    close_fds=True)
        
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

# EOF
