//============================================================================
// Name        : integritycheck.cpp
// Author      : Jamie Nadeau
// Version     :
// Copyright   : Eiffel Forum License 2.0
// Description : Checks integrity of file structure
//============================================================================

#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <iostream>
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

char * substr(char* string,int begining, int end)
{
	char* temp = new char[end-begining+1];
	strncpy(temp, string+begining, end-begining+1);
	temp[end-begining+1] = '\0';
	return temp;	
}

void checkDayDir(std::string Folder)
{
	char* s;
	DIR* d;
	struct dirent *dent;
	if((d=opendir(Folder.c_str()))==NULL)
	{
		printf("[ERROR]\t\tOpening:\"%s\"\n"); 
		exit(1);		
	}
	while((dent=readdir(d))!=NULL)
	{
	  if(std::string(dent->d_name)!="." && std::string(dent->d_name)!="..")
	  {
		switch(dent->d_type)
		{
		//case DT_:
			//printf("[WARN]\t\tFolder:\"%s\" does not belong in folder \"%s\"",dent->d_name,Folder.c_str());
			//break;
		case DT_FIFO:
			printf("[WARN]\t\tFifo:\"%s\" does not belong in folder \"%s\"\n",dent->d_name,Folder.c_str());
			break;
		default:
			if(strlen(dent->d_name)<4)
			{
			printf("[WARN]\t\tFile name invalid for \"%s\" in folder \"%s\"\n",dent->d_name,Folder.c_str());
			}
			else
			{
				printf("This is as far as I check for now come back later when I finish :)\n");
			}
		break;
		}
	  }	
	}	
}

void CheckFolder(std::string VideoFolder)
{
	DIR* d;
	if((d=opendir(VideoFolder.c_str()))==NULL)
	{
		printf("[ERROR]\t\t FOLDER DOES NOT EXIST!\n");
		return;
	}
	if(VideoFolder.at(VideoFolder.length()-1)!='/') //make sure there is a / at the end
	{
		VideoFolder+="/";
	}
	struct dirent *dent;
	struct stat st;

	while((dent=readdir(d))!=NULL)
	{
		//std::string path =dir;
		std::string d_type_out;
		int dir_day=-1;

		//As long as it's not current dir or parent folder do stuff against file/folder
		if(std::string(dent->d_name)!="." && std::string(dent->d_name)!="..")
		{	
			if(dent->d_type=DT_DIR)
			{//check name for numeric value
				dir_day = atoi(dent->d_name);
				if (dir_day==-1 or dir_day == 0)
					printf("[WARN]\t\tName:\"%s\" is not a valid directory name for projection system, it will be omitted\n",dent->d_name);
				else if(strlen(dent->d_name) < 2 or strlen(dent->d_name) > 2)
					printf("[WARN]\t\tName:\"%s\" must be a zero padded directory with the day number\n",dent->d_name);
				else
					checkDayDir(VideoFolder + std::string(dent->d_name));
			}
			else{
			switch(dent->d_type){
				case DT_UNKNOWN:
					printf("[WARN]\t\tName:\"%s\" TYPE:UNKNOWN in root video folder\n",dent->d_name);
					break;
				case DT_REG:
					printf("[WARN]\t\tName:\"%s\" Type:REGULAR FILE in root video folder\n",dent->d_name);
					break;
				case DT_FIFO:
					printf("[WARN]\t\tName:\"%s\" Type:FIFO in root video folder\n",dent->d_name);
					break;
				case DT_SOCK:
					printf("[WARN]\t\tName:\"%s\" Type:SOCKET in root video folder\n",dent->d_name);
					break;
				case DT_CHR:
					printf("[WARN]\t\tName:\"%s\" Type:CHARACTER DEVICE in root video folder\n",dent->d_name);
					break;
				case DT_BLK:
					printf("[WARN]\t\tName:\"%s\" Type:BLOCK DEVICE in root video folder\n",dent->d_name);
					break;					
			}
			
			}
		}
	}
	closedir(d);
}





int main(void) {
	std::string vidpath="/home/james/Videos";
	CheckFolder(vidpath);
	return EXIT_SUCCESS;
}
