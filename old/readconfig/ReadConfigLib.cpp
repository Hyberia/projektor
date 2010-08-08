//ReadConfigLib.cpp : Used so c or c++ may use this(wrapper)
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include "ReadConfigLib.h"
#include "configDefinitions.h"
#include "readconfig.h"

using namespace std;


//Turns Debug code on remove on production by adding // in front
//#define DEBUG


#ifdef DEBUG
int main()
{
    char* test=ReadConfParam("sampleconfig.conf",conf_COUNTDOWN);
    if(test!=NULL)
    {
        printf("%s",test);
    }
    return 0;
}
#endif

char* ReadConfParam(char* ConfigPath,char* ConfigParam)
{

    return ReadConfig::ReadConfParameter(ConfigPath,ConfigParam);
    //ReadConfig::ReadConfParameter(conf_STANDBY);
    //return ReadConfig::ReadConfParameter(conf_COUNTDOWN);
    //char test[]="   TESTING";
    //printf(ReadConfig::ShiftCharsLeft(3,(char*)test));
    //return NULL;
}
