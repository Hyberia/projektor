# Writer: Mathieu
# Date: 10 Juin 2009

# COPYRIGHT NOTICE

"""
this is the ToueiUtils module part of the Touei project.
please see http://elwillow.net/x/touei for more info.
"""

__version__ = "0.1"


def ConvertDec2Time(dTime):
    """
    Receive a decimal time (like 0930) and return a mktime with
    the current date.
    """
    
def CheckPlayer(pidFile):
    """Check if the player is still running via the pid.
    Will return TRUE if the pid is running, else return FALSE"""
    try:
        logger.debug('This message comes from one module')
        status("PlayerStillAlive: Mplayer PID: " + open(pidFile).read(), -1)
        return os.path.exists("/proc/%s" % (open(pidFile).read()))
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
