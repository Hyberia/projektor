//============================================================================
// Name        : toueid.c
// Author      : Jamie Nadeau
// Contributors:
// Version     : 0.1
// Copyright   : Eiffel Forum License 2.0
// Description : Daemon that launches the projection system
//============================================================================
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

    int rc,mpStart;
    char * ConfigValue;
    char *CurrentPath,*ConfigPath;
    FILE *fifo;
    register int i;

    ConfigPath=malloc(16);
    ConfigPath="/etc/touei.conf\0";
    CurrentPath = malloc(PATH_MAX);


    if(ConfigPath==NULL || CurrentPath==NULL)
    {
        printf("Failed to allocate memory for program\nExiting...\n");
        exit(1);
    }
    if(argc)
    {
        for(i=0;i<argc;i++)
        {
            if(strcmp(argv[i],"-c")==0 || strcmp(argv[i],"--config")==0)
            {
                //Set config path
                if (argv[i+1]==NULL){
                    goto HELP;//I don't like goto's either...
                }
                ConfigPath=realloc(ConfigPath,strlen(argv[i+1])+1);
                strcpy(ConfigPath,argv[i+1]);
                i++;
                continue;

            }

            else{
                HELP:
                printf("\nUSAGE:\n");
                printf("\ttoueid [Options..]\n\n");
                printf("\tOptions:\n");
                printf("\t  -c, --config FILE\tSpecify the path including file name for\n\t\t\t\tan alternate config file\n");
                printf("\t  -h,--help\t\tDisplay this output");

                exit(0);
            }
        }
    }
#if defined(DEBUG)
		setlogmask(LOG_UPTO(LOG_DEBUG));
		openlog(DAEMON_NAME,LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);
#else
		setlogmask(LOG_UPTO(LOG_INFO));
		openlog(DAEMON_NAME, LOG_CONS, LOG_USER);
#endif
    syslog(LOG_INFO, "[INFO] %s daemon starting up",DAEMON_NAME);




    GetExecutingPath(CurrentPath);

    CurrentPath[strlen(CurrentPath)]= '//';

    CurrentPath = realloc(CurrentPath,strlen(CurrentPath));

    ConfigValue = ReadConfParam(ConfigPath,"slave_socket");

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
        system("mplayer -idle -slave -fs -fixed-vo -input file=" + ConfigValue);
    }
    else
    {
        syslog(LOG_WARNING,"[WARN] mplayer is already started..");
    }

    //Check if toueid is already running
    rc= system("ps -C touei_run -opid=");
    if(kill(rc,0)!=0)
    {
        system(CurrentPath +"touei_run");
    }
    else
    {
        syslog(LOG_WARNING,"[WARN] touei projection system is already started.."
    }


	//Checking loop
	while(1){
		  /* mplayer check */
		  rc=-1;
		  rc=system("ps -C mplayer -opid=");
		  if (kill(rc,0)!=0)
		  {
		      //mplayer died :(
		      printf("Oh noes mplayer died");
		      syslog(LOG_WARNING,"[WARN] mplayer died");

		      //restart mplayer
		      system("mplayer -idle -slave -fs -fixed-vo -input file=" + ConfigValue);

		      //Check if touei crashed as well
		      rc=-1;
		      rc=system("ps -C touei_run -opid=");
		      if(kill(rc,0)!=0)
		      {
		          //touei died...probably jew code...
		          printf("Oh noes touei died")
		          syslog(LOG_WARNING,"[WARN] touei died");
		          system(CurrentPath +"touei_run");
		          sleep(1);
		      }
		      else
		      {
		          //Notify touei that mplayer crashed
		          kill(rc,25); //Send SIGCONT signal to toeui (19,18,25)
		      }
		  }
		  rc=-1;
		  rc=system("ps -C touei_run -opid=");
		  if(kill(rc,0)!=0)
		  {
		      //touei died...probably jew code...
		      printf("Oh noes python script died :(");
		      syslog(LOG_WARNING,"[WARN] touei died");

		      //Check if mplayer died before telling touei
		      mpStart=("ps -C mplayer -opid=");
		      if(kill(mpStart,0)!=0)
              {
                  printf("Oh noes mplayer died :(");
                  syslog("[WARN] mplayer died");
                  system("mplayer -idle -slave -fs -fixed-vo -input file=" + ConfigValue);
                  sleep(1);
              }
              //recover touei
              system(CurrentPath +"touei_run");
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


