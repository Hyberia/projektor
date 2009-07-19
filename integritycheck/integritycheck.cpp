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
#include <string>
#include <stdio.h>
#include <stdlib.h>

void CheckFolder(std::string VideoFolder)
{
	DIR* d;
	if((d=opendir(VideoFolder))==NULL)
	{
		printf("[ERROR]\t\t FOLDER DOES NOT EXIST!");
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
		std::string path =dir;

		//As long as it's not current dir or parent folder do stuff against file/folder
		if(std::string(dent->d_name)!="." && std::string(dent->d_name)!="..")
		{
			//Do stuff to folder/file
		}
		}
	}



}

int main(void) {
	std::string vidpath="~/Videos";
	CheckFolder(vidpath);
	return EXIT_SUCCESS;
}
