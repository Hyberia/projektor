#!/usr/bin/python
# Test stuff for the mkvinfo

# License: Public Domain


from subprocess import Popen, PIPE
import re
import sys

def main(file_name):
    # Open the file
    cmd = "mkvinfo " + file_name
    reg_exp = re.compile("^\|\ \+\ Duration\:\ (\d+)\.(\d+)\S+")
    times = ()
    
    # Run the command
    mkvinfo = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, close_fds=True)
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
        print "Could not find the time or is not a MKV file"
        quit(1)
    print "the file is:", sys.argv[1]
    print "Times are: %i seconds" % (seconds)
    print "           %i Microfortnight" % (seconds / 1.2096)
    print "           %i minutes and %i seconds" % (seconds/60, \
                                            seconds - 60*(seconds/60))
    if seconds - 60*(seconds/60) > 0: seconds = seconds/60 + 1
    print "           %i minutes when rounded up" % (seconds)

if __name__ == "__main__":
    main(sys.argv[1])
