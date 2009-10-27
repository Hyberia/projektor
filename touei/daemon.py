#!/usr/binpython
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

import time,signal
class ToueiDaemon():
    def __init__(self):
        self._tasks = []
        self._pidFile = '/var/run/touei_daemon.pid'
        signal.signal (signal.SIGTERM, self._signalHandler)
        signal.signal (signal.SIGHUP, self._signalHandler)
        
    def stop(self):
        self._isRunning = False
    
    def schedule(self,task,priority = 0):
        if not priority:
            self._tasks.append(task)
        else:
            self._tasks.insert(task)
            
    def run(self):
        
        self._daemonize()
        
        while(self._isRunning):
            while(len(self._tasks) and self._isRunning):
                #Execute the task
                self._tasks.pop()()
        
            if len(self._tasks):
                continue
            else:
                time.sleep(1)

    def _signalHandler(self,signal,frame):
        self._isRunning = False

    def _daemonize(self):
        """Daemonize the process
    
        @return void
        """
        psfile = open(self._pidFile, "w")
        try:
            pid = os.fork()
        except OSError,e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)
        
        if pid == 0: # first child"
            os.setsid()
            
            try:
                pid = os.fork() # fork to a second child
                if (pid != 0):
                    psfile.write(str(pid))
                    psfile.flush()
                    psfile.close()
                time.sleep(0.1)
            except OSError,e:
                raise Exception, "%s [%s]" % (e.strerror, e.errno)
                
            if(pid == 0): # the second child
                os.chdir(self.workdir)
                os.umask(self.umask)
            else:
                os._exit(0)
        else:
            os._exit(0)
        
        # Close all open file descriptors.
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = 1024
      
         # Iterate through and close all file descriptors.
        for fd in range(0, maxfd):
            try:
               os.close(fd)
            except OSError:  # ERROR, fd wasn't open to begin with (ignored)
               pass
            
        # Redirect the standard I/O file descriptors to the specified file.
      
        # This call to open is guaranteed to return the lowest file descriptor,
        # which will be 0 (stdin), since it was closed above.
        os.open(os.devnull, os.O_RDWR)  # standard input (0)
      
        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)      # standard output (1)
        os.dup2(0, 2)      # standard error (2)
        
        if os.getuid() == 0:
            try:
                userinfo = pwd.getpwnam(self._user)
                os.setgid(userinfo[3])
                os.setuid(userinfo[2])
            except OSError, e:
                pass
            
if __name__ == "__main__":
    d = ToueiDaemon()
    d.run()