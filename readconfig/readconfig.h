#ifndef READCONFIG_H_INCLUDED
#define READCONFIG_H_INCLUDED
//List of sections/config values that can be found in the config
#include <string>



namespace ReadConfig
{


    char *trim(char *str);
    char *ShiftCharsLeft(int startposition,int positions,char* str);
    char* ReadConfParameter(char* ConfigPath,char* ConfigParam);
    char *ReplaceVars(char* ConfigPath,char* ConfParam);
    bool ISSPACE_C(char* c);
}
/*class ReadConfig
{
    public:
    std::string ReadConfParameter(char* ConfigParam);

    char conf_COMMENT_CHAR;
    char conf_sec_CORE   [7];
    char  conf_sec_LOGS  [7];
    char  conf_sec_TIMING[10];
    char conf_sec_VIDEO  [7];
    char  conf_PID       [4];
    char conf_SLAVSOCK   [13];
    char conf_DAEMONLOG  [11];
    char  conf_MAINLOG   [9];
    char  conf_LEVEL     [6];
    char  conf_SEEKDELAY [11];
    char  conf_RECOVTIME [14];
    char  conf_BLOCKDURA [15];
    char  conf_LOCATION  [9];
    char conf_RECOVERY   [9];
    char  conf_STANDBY   [7];
    char conf_INTRO      [6];
    char  conf_OUTRO     [6];
    char conf_COUNTDOWN  [10];

    ReadConfig();
    ~ReadConfig();

};*/
#endif // READCONFIG_H_INCLUDED
