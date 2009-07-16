#include <sys/types.h>  /* include this before any other sys headers */
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <assert.h>
#include <syslog.h>
#include <errno.h>
#include <sys/wait.h>   /* header for waitpid() and various macros */
#include <signal.h>     /* header for signal functions */
#include <stdio.h>      /* header for fprintf() */
#include <unistd.h>     /* header for fork() */
#include <stdlib.h>   
void  ChildProcess(void);                /* child process prototype  */
void  ParentProcess(void);               /* parent process prototype */
#define DAEMON_NAME "mplayerdaemon"
#define PID_FILE "/var/run/mplayerdaemon.pid"

/***********************************************************
  Function: signal_handler
  Description: Handles signals the daemon might receive. 
               Gives the daemon enough time to properly shutdown

  Params: sig : The signal(int) received
 *********************************************************************/
void signal_handler(int sig) {
 
    switch(sig) {
        case SIGHUP:
            syslog(LOG_WARNING, "Received SIGHUP signal.");
            break;
        case SIGTERM:
            syslog(LOG_WARNING, "Received SIGTERM signal.");
            break;
        default:
            syslog(LOG_WARNING, "Unhandled signal (%d) %s", strsignal(sig));
            break;
    }
}

int  main(int argc, char *argv[])
{
#if defined(DEBUG)
	int daemonize=0;
#else
	int daemonize=1;
#endif
	
	// Setup signal handling before we start
	signal(SIGABRT, signal_handler);
    signal(SIGHUP, signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGQUIT, signal_handler);

	syslog(LOG_INFO, "[INFO] %s daemon starting up",DAEMON_NAME);

#if defined(DEBUG)
		setlogmask(LOG_UPTO(LOG_DEBUG));
		openlog(DAEMON_NAME,LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);
#else
		//setlogmask(LOG_UPTO(LOG_INFO));
		openlog(DAEMON_NAME, LOG_CONS, LOG_USER);
#endif

	/* Our process ID and Session ID */    pid_t pid, sid;

	syslog(LOG_WARNING,"[ERROR] testing error");
	daemonize=0;
	if (daemonize) {
		syslog(LOG_INFO, "[INFO] starting the daemon process");


		/* Fork off the parent */
		pid = fork();
		if (pid<0) {
			exit(EXIT_FAILURE);
		}
		/* If we got a good PID, then 
		  we can tell the parent to exit*/
		if (pid>0){
			exit(EXIT_SUCCESS);
		}
		/* Child will always have a 0 if successfully created*/

		/* Change umask so that the program will have access to all child files */
		umask(0);

		/* Create a new SID for the child process */
		sid = setsid();
		if (sid<0){
			syslog(LOG_WARNING,"[ERROR] Error while getting new session id, error code : -1");
			exit(EXIT_FAILURE);
		}

		/* Change the current working directory */
		/*
		 if ((chdir("/")) < 0){
			syslog(LOG_ERR,"Error while changing directory error code : -1");
			 exit(EXIT_FAILURE);
		 }

		 */

		/* Close out the standard file descriptors 
		   Because daemon won't be accepting input from console */
		close(STDIN_FILENO);
		close(STDOUT_FILENO);
		close(STDERR_FILENO);
		
	}

	while(1){
          int rc=system("ps -C mplayer -opid=");
						
          rc = WEXITSTATUS(rc); /* Check if mplayer is running */
		  printf("I was here pid: %d\n",rc);

		/*if mplayer quits unexpectedly */
		if(rc > 0 ){
		   
		         launchmplayer();
	             sleep(2);
              }

     }

	/* if loop breaks daemon exits*/
	syslog(LOG_INFO, "%s daemon exiting",DAEMON_NAME);

	exit(0);
}

void launchmplayer(void)
{
     system("mplayer ~/G-Anime/mplayer-daemon/test.avi");
     return;
}

