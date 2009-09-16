#!/usr/bin/python
# Writer: Mathieu,Martin
# Date: 10 Juin 2009
#
# Eiffel Forum License, version 2
#
# 1. Permission is hereby granted to use, copy, modify and/or
#    distribute this package, provided that:
#       * copyright notices are retained unchanged,
#       * any distribution of this package, whether modified or not,
#         includes this license text.
# 2. Permission is hereby also granted to distribute binary programs
#    which depend on this package. If the binary program depends on a
#    modified version of this package, you are encouraged to publicly
#    release the modified version of this package.
#
# THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.

"""
this is the Playlist module part of the Touei project.
please see http://elwillow.net/touei for more info.
"""

__author__ = "Mathieu Charron"
__license__ = "Eiffel Version 2"
__version__ = "0.1"
__revision__ = ""


import sqlite3 as sqlite
import os,sys,datetime
from mkvutils import MkvUtils

class DBUnavailableException(Exception): pass
class DBExistsException(Exception): pass
class NoFilesException(Exception): pass

class PlayList():
    def __init__(self):
        self._db = None
        self._schema = []
        self._schema.append('''create table presentations(
                            id integer primary key autoincrement,
                            date int,
                            file varchar(255),
                            title varchar(255),
                            duration int
                            )''')
        
        self._schema.append('''create table fillers(
                            id integer primary key autoincrement,
                            file varchar(255),
                            title varchar(255),
                            duration int
                            )''')
        
        self._queries = {}
        self._queries['store'] = 'insert into presentations (date,file,title,duration) values(?,?,?,?);'
        
    def _getFormattedTime(self):
        return datetime.datetime.now().strftime("%H%M")
        
    def _getCurDay(self):
        return datetime.datetime.now().strftime("%d");
    
    def _getFormattedDate(self):
        return datetime.datetime.now().strftime("%Y%m%d")
        
    def _createDb(self):
        '''Create the database if it is not already initialized.'''
        
        if self._db:
            raise DBExistsException()
        
        #Create the database in RAM instead of on-disk.
        try:
            self._db = sqlite.connect(":memory:")
        except Exception,e:
            raise e
        
        cursor = None
        try:
            cursor = self._db.cursor()
            for table in self._schema:
                cursor.execute(table)
            self._db.commit()
        except Exception,e:
            self._db.rollback()
            raise e
        finally:
            if cursor: cursor.close()
            
        return True
    
    def _closeDb(self):
        '''Close the database connection'''
        if not self._db:
            raise DBUnavailableException()
        try:
            self._db.close()
        except Exception,e:
            return False
        self._db = None
        return True
    
    def _storeSchedule(self,schedule):
        cursor = None
        try:
            cursor = self._db.cursor()
        except Exception,e:
            print e
            return False
        
        for date in schedule.keys():
            for time in schedule[date].keys():
                fdate = schedule[date][time]['date']
                file = schedule[date][time]['file']
                title = schedule[date][time]['title']
                duration = schedule[date][time]['duration']
                try:
                    cursor.execute(self._queries['store'],(fdate,file,title,duration,))
                except Exception,e:
                    print e
                    cursor.close()
                    self._db.rollback()
                    return False
        try:
            cursor.close()
            self._db.commit()
        except Exception,e:
            print e
            return False
        return True
                
    def _parseFiles(self):
        '''Parses files and prepare them for playback.'''
        
        #rootDir = #Config# + "/" + self._getCurDay()
        rootDir = '/home/masom/dev/videos'
        rootDirLen = len(rootDir)
        presentations = self._getFiles(rootDir)
        
        if len(presentations.keys()) == 0:
            raise NoFilesException()
        
        schedule = {}
        mkvUtils = MkvUtils()
        for path in presentations.keys():
            #Get the relative path from the root dir.
            # rootDirLen + 1 removes the slash between the relative path and the "root"
            relPath = path[rootDirLen + 1:]
            subFolders = relPath.split('/')
            if len(subFolders) > 1:
                print "Dropping: " + relPath
                print "Reason: Is a subfolder"
                continue
            
            
            try:
                int(relPath)
            except Exception,e:
                #We got something that is not a integer
                print "Dropping: " + relPath
                print "Reason: Not a number"
                continue
            
            day = relPath
            
            if len(presentations[path]) == 0:
                #Nothing for that day
                print "Nothing to be added for " + relPath
                continue
            
            
            schedule[day] = {}
            for video in presentations[path]:
                parts = video.split('.')
                if len(parts) != 3:
                    print "Dropping: "+ video
                    print "Reason: Filename " + video + " could not be splitted."
                    continue
                
                if schedule[day].has_key(parts[0]):
                    print "Conflict: Filename: " + video + " is in conflict with " + schedule[day][parts[0]]
                else:
                    title = parts[1].replace('_',' ').strip('[]')
                    file = path + "/" + video
                    
                    duration = mkvUtils.mkvTime(file)
                    
                    presentationInfo = {}
                    presentationInfo['date'] = self._getFormattedDate() + parts[0]
                    presentationInfo['file'] = file
                    presentationInfo['title'] = title
                    presentationInfo['duration'] = duration
                    schedule[day][parts[0]] = presentationInfo
            
        return schedule
    
    def _getFiles(self,dir):
        '''Get all the mkv files from dir (and bellow)'''
        videos = {}
        for path, dirs, files in os.walk(dir):
        
            for file in files:
                if not file.endswith('.mkv'):
                    continue
                
                if not path in videos.keys():
                    videos[path] = []
                    
                videos[path].append(file)
                
        return videos
p = PlayList()
p._createDb()
schedule = p._parseFiles()
print schedule
p._storeSchedule(schedule)