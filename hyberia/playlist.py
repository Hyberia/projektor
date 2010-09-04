#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
this is the Playlist module part of the HYBERIA project.
please see http://hyberia.org for more info.
"""

__author__ = "G-Anime"
__license__ = "Eiffel Version 2"
__version__ = "0.3.2"
__contributors__= "Mathieu Charron, Martin Samson"

import os,sys,datetime,json,logging

# Instanciate the logging
module_logger = logging.getLogger("hyberia.playlist")

class PlayListNotFoundException(Exception): pass
class PlayListImportErrorException(Exception): pass
class PlayListFileNotFoundException(Exception): pass
class PlayListVIBNotSetException(Exception): pass

class PlayList():
    def __init__(self, videoInfoBackend = None):
        '''videoInfoBackend Hyberia VIB API compatible backend class instance'''
        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.playlist.Playlist")
        self.logger.info("Creating instance")
        
        if videoInfoBackend == None:
            print ("CRITICAL: HVIB not set")
            print("")
            raise PlayListVIBNotSetException()
        
        #Look for HVIB_API_VERSION attr
        try:
            getattr(videoInfoBackend, "HVIB_API_VERSION")
        except AttributeError:
            print ("CRITICAL: Non-HVIB compliant videoInfoBackend.")
            print("")
            raise PlayListVIBNotSetException()
        
        #Verify it matches required version
        if not videoInfoBackend.HVIB_API_VERSION >= 1:
            print ("CRITICAL: Incompatible HVIB")
            print("")
            raise PlayListVIBNotSetException()
            
        self.__videoInfoBackend = videoInfoBackend
        self._playList = {}
        
    def __createBlock(self, runDate = 0, runTime = 0, name = "DefaultBlockName" , description = ""):
        block = {}
        block['runDate'] = runDate
        block['runTime'] = runTime
        block['totalDuration'] = 0
        block['name'] = name
        block['description'] = description
        block['parts'] = []
        return block
    
    def __createPart(self, resource):          
        part = {}
        
        #The video file name
        part['file'] = resource['file']
        part['name'] = resource['name']
        
        #Duration in seconds
        part['duration'] = self.__videoInfoBackend.HVIB_RunningTime(part['file'])
        
        #Will hold when to play the file as a datetime format (yyyymmddhhiiss)
        part['playAt'] = 0
        return part
    
    def load(self, playListFile):
        if not os.path.exists(playListFile):
            self.logger.critical("Playlist file not found.");
            raise PlayListNotFoundException()
        
        try:
            playListStruct = json.load(open(playListFile, "r"))
        except Exception as e:
            print(e)
            print("This is a parsing error. Strings in json must be delimited with \" instead of ' ")
            raise PlayListImportErrorException()
        
        for elem in ["blocks","resources"]:
            if not elem in playListStruct:
                print(elem + " not found")
                raise PlayListImportErrorException()

        
        for resource in playListStruct['resources']:
            if not 'file' in playListStruct['resources'][resource]:
                print("CRITICAL: Resource "+ str(resource) +" has no file attribute");
                raise PlayListImportErrorException()
                
            if not os.path.exists(playListStruct['resources'][resource]['file']):
                print("CRITICAL: Resource " + str(resource) + " file ("+ playListStruct['resources'][resource]['file'] +") does not exists")
                raise PlayListImportErrorException()
                
                
                
        for dateBlock in playListStruct["blocks"]:
            if self._playList.has_key(dateBlock):
                print("ERROR: Duplicate date blocks")
                raise PlayListImportErrorException()
            
            prev_block_id = 0
            
            for timeBlock in playListStruct["blocks"][dateBlock]:
                blockStruct = playListStruct["blocks"][dateBlock][timeBlock]
                
                block = self.__createBlock(dateBlock,timeBlock,blockStruct["name"],blockStruct["description"])
                for part in blockStruct['parts']:
                    part = self.__createPart(part)
                    block['parts'].append(part)
                    block['totalRunTime'] += part['duration']
                
                blockId = dateBlock * 1000 + timeBlock
                if prev_block_id > blockId:
                    print("Critical: Block duration overlapping at " + str(blockId))
                    raise PlayListImportErrorException()
                self._playList[blockId].append(block)
                
        print repr(self._playList);

    def _getFormattedDateTime(self, format = "%Y%m%d%H%M"):
        return datetime.datetime.now().strftime(format)

    def _getFormattedTime(self):
        return datetime.datetime.now().strftime("%H%M")

    def _getCurDay(self):
        return datetime.datetime.now().strftime("%d");

    def _getFormattedDate(self, format = "%Y%m%d"):
        return datetime.datetime.now().strftime(format)

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
    import mkvutils
    m = mkvutils.MkvUtils()
    p = PlayList(m)
    p.load('../cfg/playlist.json')
    
    print p._getFormattedDateTime()
    print "playlist", p.getPlayList()
    print "get", p.get()
    print "getNext", p.getNext()
    print "getPrevious", p.getPrevious()
