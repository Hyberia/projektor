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
#include <unistd.h>     /* header for fork(), getcwd() */
#include <stdlib.h>
#include <limits.h>
//void  ChildProcess(void);                /* child process prototype  */
//void  ParentProcess(void);               /* parent process prototype */
#define DAEMON_NAME "toueid"
#define PID_FILE "/var/run/toueid.pid"

/***********************************************************
  Function: signal_handler
  Description: Handles signals the daemon might receive.
               Gives the daemon enough time to properly shutdown

  Params: sig : The signal(int) received
 *********************************************************************/
void signal_handler(int sig) {


    //signal(SIGABRT, signal_handler);
    //signal(SIGHUP, signal_handler);
    //signal(SIGTERM, signal_handler);
    //signal(SIGINT, signal_handler);
   // signal(SIGQUIT, signal_handler);
    switch(sig) {

        case SIGABRT:
            syslog(LOG_WARNING, "Received SIGABRT signal.");
            exit(0);
            break;
        case SIGQUIT:
            syslog(LOG_WARNING, "Received SIGQUIT signal.");
            exit(0);
            break;
        case SIGHUP:
            syslog(LOG_WARNING, "Received SIGHUP signal.");
            exit(0);
            break;
        case SIGTERM:
            syslog(LOG_WARNING, "Received SIGTERM signal.");
            exit(0);
            break;
        case SIGINT:
            syslog(LOG_WARNING, "Received SIGINT signal.");
            exit(0);
            break;
        default:
            syslog(LOG_WARNING, "Unhandled signal (%d) %s", strsignal(sig));
            exit(-1);
            break;
    }
}

int  main(int argc, char *argv[])
{
   //char lol[PATH_MAX+1];

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
		setlogmask(LOG_UPTO(LOG_INFO));
		openlog(DAEMON_NAME, LOG_CONS, LOG_USER);
#endif

	/* Our process ID and Session ID */
    pid_t pid, sid;
    int rc,mpStart;

	//daemonize=0;
	//if (daemonize) {


	//	/* Fork off the parent */
	//	pid = fork();
	//	if (pid<0) {
	//		exit(EXIT_FAILURE);
	//	}
	//	/* If we got a good PID, then
	//	  we can tell the parent to exit*/
	//	if (pid>0){
	//		exit(EXIT_SUCCESS);
	//	}
	//	/* Child will always have a 0 if successfully created*/

	//	/* Change umask so that the program will have access to all child files */
	//	umask(0);

	//	/* Create a new SID for the child process */
	//	sid = setsid();
	//	if (sid<0){
	//		syslog(LOG_WARNING,"[ERROR] Error while getting new session id, error code : -1");
	//		exit(EXIT_FAILURE);
	//	}

	//	/* Change the current working directory */
	//	/*
	//	 if ((chdir("/")) < 0){
	//		syslog(LOG_ERR,"Error while changing directory error code : -1");
	//		 exit(EXIT_FAILURE);
	//	 }

	//	 */

	//	/* Close out the standard file descriptors
	//	   Because daemon won't be accepting input from console */
	//	close(STDIN_FILENO);
	//	close(STDOUT_FILENO);
	//	close(STDERR_FILENO);
	//
	//} /* End Daemonization */
 system("gedit");
	//Checking loop
	while(1){
		  /* mplayer check */
		  rc=-1;
		  rc=system("ps -C mplayer -opid=");
		  if (kill(rc,0)!=0)
		  {
		      //mplayer died :(
		 //    printf("Oh noes mplayer died");

		  }
		  rc=-1;
		  rc=system("ps -C run.py -opid=");
		  if(kill(rc,0)!=0)
		  {
		      //Python script died :(
		   //   printf("Oh noes python script died :(");
		  }
		  sleep(10);
	}


     //     rc = WEXITSTATUS(rc); /* Check if mplayer is running */
	//	  printf("I was here pid: %d\n",rc);

		  /*if mplayer quits unexpectedly */
	//	  if(rc > 0 ){
	//	         launchmplayer();
	//             sleep(2);
    //          }


		  /* Check for touei */
		  //TODO: Check for touei

		  //GetExecutingPath(&lol);
		  //printf("%s",lol);
   //  }

	/* if loop breaks daemon exits*/
	syslog(LOG_INFO, "[WARNING] %s daemon exiting checking loop: NOT NORMAL",DAEMON_NAME);

	exit(0);
}
//Gets the directory in which the application is running
void GetExecutingPath(char* buffer)
{
	if(readlink("/proc/self/exe",buffer,sizeof(buffer)-1)==-1)
		printf('Error reading symlink');

}
void launchtouei(void)
{
	//TODO:Launch touei
	char CurrentPath[PATH_MAX + 1];
	GetExecutingPath(*CurrentPath);
}
void launchmplayer(void)
{
	//TODO: Run touei in recovery mode
     system("mplayer ~/G-Anime/mplayer-daemon/test.avi");
     return;
}


