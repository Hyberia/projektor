#include "readconfig.h"
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "configDefinitions.h"

using namespace std;

char* ReadConfig::ReadConfParameter(char* ConfigPath,char* ConfigParam)
{
    FILE *f;
    char s[1000];

    f=fopen(ConfigPath,"r");

    if(!f)
    {
        return "ERR404";
    }
    while(fgets(s,1000,f)!=NULL) //Get Line from config
    {
        trim((char *)s);
        bool NonIgnore=(!(s[0]==conf_COMMENT_CHAR || s[0]=='[' || s[0]=='\n' || s[0]=='\r'));
         if(NonIgnore)//Is not a comment,section or whitespace(new line)
        {
            char assmbly[16];
            int i;

            for(i=0;;i++)
            {
                if(s[i]==conf_EQUAL_CHAR)
                {break;}
                assmbly[i]=s[i];
            }
            assmbly[i]='\0'; //Add Null Termination
            if(strcmp(assmbly,ConfigParam)==0)
            {

                ShiftCharsLeft(0,strlen(assmbly)+1,(char*)s);
                trim((char*)s);
                ReplaceTrailGarbage((char *)s);

                //Replace variables in string
                int replaced = ReplaceVars(ConfigPath,(char*)s);


                char* ParamValue=new char[strlen(s)];
                ParamValue[0]='/0';
                fclose(f);
                strcpy(ParamValue,s);
                return ParamValue;
            }

        }
        s[0]='\0';
    }
    fclose(f);
    return NULL;
}

//Replaces variables defined in Parameter by the actual value
int ReadConfig::ReplaceVars(char* ConfigPath,char* ConfParam)
{
    for(int i=0;ConfParam[i]!='\0';i++)
    {
        if(ConfParam[i]=='%')
        {
            if(ConfParam[i+1]=='(')
            {
                char param[100];
                int j=i+2;//Skip "%("
                int k=0;
                //loop until closing bracket or end of string
                while(ConfParam[j]!=')' && ConfParam[j]!='\0')
                {
                    param[k]=ConfParam[j];
                    j++;
                    k++;
                }
                param[k]='\0';
                char* tmp=ReadConfParameter(ConfigPath,(char*)param);
                if(i==0)//Variable at start of string
                {
                    char tmpcpy[1000];
                    tmpcpy[0]='\0';
                    ShiftCharsLeft(0,j+1,ConfParam);
                    if(tmp!=NULL){
                       strcat(tmpcpy,tmp);
                    }

                    strcat(tmpcpy,ConfParam);
                    strcpy(ConfParam,tmpcpy);
                    return 1;
                }
                else //Variable in the middle of string
                {


                }
                free(tmp);
            }
        }
    }
    return 0;
}

//Removes trailing \r \n that may be present
void ReadConfig::ReplaceTrailGarbage(char* str)
{
    for(int i=0;i<strlen(str);i++)
    {
        if(str[i]=='\r' || str[i] == '\n')
        {
            str[i]='\0';
            return;
        }
    }
}

//Shifts all characters after startposition by the specified # of positions to the left
char *ReadConfig::ShiftCharsLeft(int startposition,int positions,char* str)
{
    int i,j;
    i=startposition;
    j=positions;
    while(str[j]!='\0')
    {
        str[i]=str[j];
        i++;
        j++;
    }
    str[i]='\0';
    return str;
}
//Trims whitespaces from start
char *ReadConfig::trim(char *str)
{
    int i=0;
    int a=0;

    if (str==NULL)
    {return NULL;}
    if(str[0]=='\0')
    {return str;}


    while(str[i]!='\0')
    {
        if(!ISSPACE_C(&str[i]))
        {
            while(str[i]!='\0')
            {
                str[a]=str[i];
                a++;
                i++;
            }
        }
        else{
        i++;
        }
    }
    if(a<i)//There were spaces
    {str[a]='\0';} //Add Null termination
    return str;
}
bool ReadConfig::ISSPACE_C(char* c)
{
    switch(c[0])
    {
        case '\t':
            return true;
        break;
        case ' ':
            return true;
        break;
        default:
            return false;
        break;
    }
}
//string ReadConfParameter(char* ConfigSection,char* ConfigParam)
//{}

