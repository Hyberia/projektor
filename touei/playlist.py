#!/usr/bin/env python
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

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.2"
__revision__ = "47"
__contributors__= "Mathieu Charron, Martin Samson"


import sqlite3 as sqlite
import os,sys,datetime

# Instanciate the logging
import logging
module_logger = logging.getLogger("touei.playlist")

class DBUnavailableException(Exception): pass
class DBExistsException(Exception): pass
class NoFilesException(Exception): pass


class PlayList():
    def __init__(self, mkv):
        # Instanciate the logger
        self.logger = logging.getLogger("touei.playlist.Playlist")
        self.logger.info("Creating instance")

        self._MkvUtils = mkv
        self._db = None
        self._schema = []
        self._schema.append('''create table presentations(
                            id integer primary key autoincrement,
                            datetime_start integer,
                            datetime_end integer,
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
        self._queries['store'] = 'insert into presentations (datetime_start,datetime_end,file,title,duration) values(?,?,?,?,?);'
        self._queries['getAll'] = 'select * from presentations order by datetime_start ASC;'
        self._queries['getNext'] = 'select * from presentations where datetime_start > ? order by datetime_start ASC;'
        self._queries['getPrevious'] = 'select * from presentations where datetime_start < ? order by datetime_start ASC;'
        self._queries['getCurrent'] = 'select * from presentations where datetime_start <= ? and datetime_end >= ?';
        self._rootDir = None
        self._createDb()

    def load(self,rootDir):
        """Load a playlist from a directory.
        """
        self._rootDir = rootDir
        self._storeSchedule(self._parseFiles())



    def getPlayList(self):
        cursor = None
        try:
            cursor = self._db.cursor()
            rows = cursor.execute(self._queries['getAll']).fetchall()
            cursor.close();
        except Exception,e:
            print e
            return None
        self.logger.debug("rows = " + str(rows))
        return rows

    def get(self):
        """Find a playable file for the current datetime and return it"""
        video = None
        date = self._getFormattedDateTime()
        self.logger.debug("date = " + date)
        try:
            cursor = self._db.cursor()
            video = cursor.execute(self._queries['getCurrent'], (date,date)).fetchone()
            self.logger.debug("video = " + str(video))
        except Exception,e:
            print e
            return False
        finally:
            cursor.close()

        return video

    def getPrevious(self):
        """Find what was scheduled to previously play.
        """

        current = self.get()
        if current:
            datetime_start = current['datetime_start'] - 1
        else:
            datetime_start = self._getFormattedDateTime()

        video = None
        try:
            cursor = self._db.cursor()
            video = cursor.execute(self._queries['getPrevious'], (datetime_start,)).fetchone()
        except Exception,e:
            print e
            return False
        finally:
            cursor.close()

        return video

    def getNext(self):
        """Find what is coming up.
        """

        video = None
        try:
            cursor = self._db.cursor()
            video = cursor.execute(self._queries['getNext'], (self._getFormattedDateTime(),)).fetchone()
        except Exception,e:
            print e
            return False
        finally:
            cursor.close()

        return video

    def _getFormattedDateTime(self, format = "%Y%m%d%H%M"):
        return datetime.datetime.now().strftime(format)

    def _getFormattedTime(self):
        return datetime.datetime.now().strftime("%H%M")

    def _getCurDay(self):
        return datetime.datetime.now().strftime("%d");

    def _getFormattedDate(self, format = "%Y%m%d"):
        return datetime.datetime.now().strftime(format)

    def _createDb(self):
        """Create the database if it is not already initialized.
        """

        if self._db:
            raise DBExistsException()

        #Create the database in RAM instead of on-disk.
        try:
            self._db = sqlite.connect(":memory:")
            self._db.row_factory = sqlite.Row
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
        """Close the database connection.
        """
        if not self._db:
            raise DBUnavailableException()
        try:
            self._db.close()
        except Exception,e:
            self.logger.info("Could not close database")
            return False
        self._db = None
        self.logger.info("Closing database")
        return True

    def _storeSchedule(self,schedule):
        cursor = None
        try:
            cursor = self._db.cursor()
        except Exception,e:
            print e
            return False
        # Enable for debuging purposes
        #print schedule
        for date in schedule.keys():
            for time in schedule[date].keys():
                datetime_start = schedule[date][time]['datetime_start']
                datetime_end = schedule[date][time]['datetime_end']
                file = schedule[date][time]['file']
                title = schedule[date][time]['title']
                duration = schedule[date][time]['duration']
                try:
                    self.logger.debug("ADDING: " + str(schedule[date][time]))
                    cursor.execute(self._queries['store'],(datetime_start,datetime_end,file,title,duration,))
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
        """Parses files and prepare them for playback.
        """
        rootDirLen = len(self._rootDir)
        self.logger.debug("rootDirLen = " + str(rootDirLen))
        presentations = self._getFiles(self._rootDir)
        self.logger.debug("presentations = " + str(presentations))
        if len(presentations.keys()) == 0:
            raise NoFilesException()

        schedule = {}
        for path in presentations.keys():
            #Get the relative path from the root dir.
            # rootDirLen + 1 removes the slash between the relative path and the "root"
            self.logger.debug("path = " + str(path))
            relPath = path[rootDirLen + 0:]
            self.logger.debug("relPath = " + str(relPath))
            subFolders = relPath.split('/')
            self.logger.debug("subFolders = " + str(subFolders))
            if len(subFolders) > 1:
                self.logger.debug("Dropping: " + relPath)
                self.logger.debug("Reason: Is a subfolder")
                continue


            try:
                int(relPath)
            except Exception,e:
                #We got something that is not a integer
                self.logger.debug("Dropping: " + relPath)
                self.logger.debug("Reason: Not a number")
                continue

            day = relPath

            if len(presentations[path]) == 0:
                #Nothing for that day
                self.logger.info("Nothing to be added for " + relPath)
                continue


            videoCount = 0
            schedule[day] = {}
            for video in presentations[path]:
                parts = video.split('.')
                if len(parts) != 3:
                    self.logger.info("Dropping: "+ video)
                    self.logger.info("Reason: Filename " + video + " could not be splitted.")
                    continue

                if schedule[day].has_key(parts[0]):
                    self.logger.error("Conflict: Filename: " + str(video) + " is in conflict with " + str(schedule[day][parts[0]]))
                else:
                    title = parts[1].replace('_',' ').strip('[]')
                    file = path + "/" + video

                    duration = self._MkvUtils.mkvTime(file)

                    presentationInfo = {}
                    presentationInfo['datetime_start'] = self._getFormattedDate("%Y%m") + day + parts[0]
                    presentationInfo['datetime_end'] = int(presentationInfo['datetime_start']) + (duration / 60)
                    presentationInfo['file'] = file
                    presentationInfo['title'] = title
                    presentationInfo['duration'] = duration
                    schedule[day][parts[0]] = presentationInfo
                    videoCount += 1

            self.logger.info("" + str(videoCount) + " videos in " + str(path))
        return schedule

    def _getFiles(self,dir):
        """Get all the mkv files from dir (and bellow)
        """
        videos = {}
        for path, dirs, files in os.walk(dir,True,None,True):

            for file in files:
                if not file.endswith('.mkv'):
                    continue

                if not path in videos.keys():
                    videos[path] = []

                videos[path].append(file)

        return videos

if __name__ == "__main__":
    print "##### DEBUG ######"
    p = PlayList()
    p.load('/home/elwillow/G-Anime/screens/track3')
    print p._getFormattedDateTime()
    print "playlist", p.getPlayList()
    print "get", p.get()
    print "getNext", p.getNext()
    print "getPrevious", p.getPrevious()
