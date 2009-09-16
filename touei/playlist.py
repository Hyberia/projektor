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

__version__ = "0.1"


import sqlite3 as sqlite
import os,sys,datetime

class DBUnavailableException(Exception): pass
class DBExistsException(Exception): pass

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
        
        self._date = datetime.datetime.now()
        
    def _getFormattedTime(self):
        return self._date.strftime("%H%M")

    def _CreateDb(self):
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
    
    def _CloseDb(self):
        '''Close the database connection'''
        if not self._db:
            raise DBUnavailableException()
        try:
            self._db.close()
        except Exception,e:
            return False
        
        self._db = None
        return True
    
    def _parseFiles(self):
        '''Parses files and prepare them for playback.'''
        presentations = self._getFiles('/home/masom/video')
        
        if len(presentations.keys()) == 0:
            raise NoFilesException()
        
        print presentations
        
    
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