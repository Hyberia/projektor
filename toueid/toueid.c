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
#include "ReadConfigLib.h"
#define PATH_MAX 4096
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

#if defined(DEBUG)
		setlogmask(LOG_UPTO(LOG_DEBUG));
		openlog(DAEMON_NAME,LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);
#else
		setlogmask(LOG_UPTO(LOG_INFO));
		openlog(DAEMON_NAME, LOG_CONS, LOG_USER);
#endif
    syslog(LOG_INFO, "[INFO] %s daemon starting up",DAEMON_NAME);

	/* Our process ID and Session ID */
    int rc,mpStart;
    char * ConfigValue;
    char CurrentPath[PATH_MAX];
    FILE *fifo;

    GetExecutingPath(&CurrentPath);

    CurrentPath[strlen(CurrentPath)]= '//';

    ConfigValue = ReadConfParam("/home/james/G-Anime/DaeNity/touei.DaeNity/readconfig/sampleconfig.conf","slave_socket");

    //ReadConfParam could not find configuration file
    if( strcmp(ConfigValue,"ERR404")==0)
    {
        printf("Could not find the configuration(touei.conf) file");
        syslog(LOG_ERR,"[ERR] Could not find the configuration file");
        exit(-1);
    }

    //Check if mplayer fifo file exits
    fifo =fopen(ConfigValue,"r")
    if(!fifo)
    {
        system("mkfifo " + ConfigValue);
    }
    else
    {
        fclose(fifo)
    }

    //Check if mplayer is already running
    mpStart = system("ps -C mplayer -opid=");
    if(kill(mpStart,0)!=0)
    {
        syslog(LOG_WARNING,"[WARN] mplayer is already started..");
    }
    else
    {
        system("mplayer -slave -idle -input file=" + ConfigValue);
    }

    //Check if toueid is already running
    rc= system("ps -C run.py -opid=");
    if(kill(rc,0)!=0)
    {
        syslog(LOG_WARNING,"[WARN] touei projection system is already started.."
    }
    else
    {
        system(CurrentPath +"run.py");
    }


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


	/* if loop breaks daemon exits*/
	syslog(LOG_INFO, "[WARNING] %s daemon exiting checking loop: NOT NORMAL",DAEMON_NAME);

	exit(0);
}
//Gets the directory in which the application is running
void GetExecutingPath(char* buffer)
{
	if(readlink("/proc/self/exe",buffer,PATH_MAX)==-1)
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


