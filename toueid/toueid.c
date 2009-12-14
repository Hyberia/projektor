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
    char tmpCath[255];
    char *tmpCat;
    char *Exec;
    register int i;

    tmpCat = &tmpCath;

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
        for(i=1;i<argc;i++)
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
                printf("\t  -h,--help\t\tDisplay this output\n");

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
    CurrentPath[strlen(CurrentPath)-6]='\0';
//    CurrentPath[strlen(CurrentPath)]= '//';

    CurrentPath = realloc(CurrentPath,strlen(CurrentPath)+1);
    CurrentPath[strlen(CurrentPath)]='\0';

    ConfigValue = ReadConfParam(ConfigPath,"slave_socket");
    ConfigValue[strlen(ConfigValue)]='\0';
    printf("Read config");

    //ReadConfParam could not find configuration file
    if( strcmp(ConfigValue,"ERR404")==0)
    {
        printf("Could not find the configuration(touei.conf) file\n");
        syslog(LOG_ERR,"[ERR] Could not find the configuration file");
        exit(-1);
    }

    //Check if mplayer fifo file exits
    //fifo =fopen(ConfigValue,"r");
    printf("Creating fifo");
    strcpy(tmpCat,"mkfifo ");
    strcat(tmpCat,ConfigValue);
    system(tmpCat);
    tmpCat[0]='\0';
   /* if((fifo=fopen(ConfigValue,"r"))==NULL)
    {
        strcpy(tmpCat,"mkfifo ");
        //tmpCat="mkfifo ";
        strcat(tmpCat,ConfigValue);
        system( tmpCat);
        tmpCat[0]='\0';
    }
    else
    {
        fclose(fifo);
    }*/

    //Get PID
    mpStart=GetPID("ps -C mplayer -opid=");
    //Check if mplayer is already running
    //mpStart = system("ps -C mplayer -opid=");
    if((kill(mpStart,0)!=0) || mpStart == -1)
    {
        strcpy(tmpCat,"mplayer -idle -slave -fs -fixed-vo -input file=");
        strcat(tmpCat,ConfigValue);
        strcat(tmpCat, " &");
        Exec = malloc(strlen(tmpCat)+1);
        strcpy(Exec,tmpCat);
        system(Exec);
        free(Exec);
        tmpCat[0]='\0';
    }
    else
    {
        syslog(LOG_WARNING,"[WARN] mplayer is already started..");
    }

    //Check if toueid is already running
    rc= GetPID("ps -C touei_run -opid=");
    if((kill(rc,0)!=0) || rc==-1)
    {
        strcpy(tmpCat, CurrentPath);
        strcat(tmpCat,"touei_run &");
        system( tmpCat);
        tmpCat[0]='\0';
    }
    else
    {
        syslog(LOG_WARNING,"[WARN] touei projection system is already started..\n");
    }


	//Checking loop
	while(1){
		  /* mplayer check */
		  rc=-1;
		  rc=GetPID("ps -C mplayer -opid=");
		  if ((kill(rc,0)!=0) || rc==-1)
		  {
		      //mplayer died :(
		      printf("Oh noes mplayer died\n");
		      syslog(LOG_WARNING,"[WARN] mplayer died");

		      //restart mplayer
		      strcpy(tmpCat,"mplayer -idle -slave -fs -fixed-vo -input file=");
              strcat(tmpCat,ConfigValue);
              strcat(tmpCat, " &");
              Exec = malloc(strlen(tmpCat)+1);
              strcpy(Exec,tmpCat);
              system(Exec);
              free(Exec);
              tmpCat[0]='\0';

		      //Check if touei crashed as well
		      rc=-1;
		      rc=GetPID("ps -C touei_run -opid=");
		      if((kill(rc,0)!=0) || rc==-1)
		      {
		          //touei died...probably jew code...
		          printf("Oh noes touei died\n");
		          syslog(LOG_WARNING,"[WARN] touei died");
                  strcpy(tmpCat, CurrentPath);
                  strcat(tmpCat,"touei_run &");
                  system( tmpCat);
                  tmpCat[0]='\0';
		          sleep(1);
		      }
		      else
		      {
		          //Notify touei that mplayer crashed
		          kill(rc,25); //Send SIGCONT signal to toeui (19,18,25)
		      }
		  }
		  rc=-1;
		  rc=GetPID("ps -C touei_run -opid=");
		  if((kill(rc,0)!=0) || rc==-1)
		  {
		      //touei died...probably jew code...
		      printf("Oh noes python script died :(\n");
		      syslog(LOG_WARNING,"[WARN] touei died");

		      //Check if mplayer died before telling touei
		      mpStart=GetPID("ps -C mplayer -opid=");
		      if((kill(mpStart,0)!=0) || mpStart==-1)
              {
                  printf("Oh noes mplayer died :(\n");
                  syslog(LOG_WARNING,"[WARN] mplayer died");
                  strcpy(tmpCat,"mplayer -idle -slave -fs -fixed-vo -input file=");
                  strcat(tmpCat,ConfigValue);
                  strcat(tmpCat, " &");
                  Exec = malloc(strlen(tmpCat)+1);
                  strcpy(Exec,tmpCat);
                  system(Exec);
                  free(Exec);
                  tmpCat[0]='\0';
                  sleep(1);
              }
              //recover touei
              strcpy(tmpCat, CurrentPath);
              strcat(tmpCat,"touei_run &");
              system( tmpCat);
              tmpCat[0]='\0';

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

int GetPID(char* command){
    int iPID;
    char PID[20];
    FILE *fp;
    //Get PID
    fp=popen(command,"r");
    if(fp==NULL)
    {
        printf("Failed to run pipe for PID");
        syslog(LOG_WARNING,"[ERR] Could not pipe to obtain pid");
        exit -1;
    }

    if(fgets(PID,sizeof(PID)-1,fp) != NULL)
    {
        iPID= atoi(&PID);
    }
    else{ iPID=-1;}
    pclose(fp);

    return iPID;
}


