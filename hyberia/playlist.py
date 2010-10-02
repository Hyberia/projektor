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

import os,sys,datetime,json,logging,time

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
        self._playList = []
        self._blocks = {}

    def __createBlock(self, id = 0, runDate = 0, runTime = 0, name = "DefaultBlockName" , description = ""):
        block = {}
        block['id'] = id
        block['runDate'] = int(runDate)
        block['runTime'] = int(runTime)
        block['totalRunTime'] = 0
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
        '''Load the playlist file into memory'''

        # Get the playlist file
        playListFile = playListFile + "/playlist.json"
        self.logger.debug("Loading playlist from %s" % (playListFile,))

        #Verify the playlist file exists
        if not os.path.exists(playListFile):
            self.logger.critical("Playlist file not found.");
            raise PlayListNotFoundException()

        #Attempt to parse the playlist file
        try:
            playListStruct = json.load(open(playListFile, "r"))
        except Exception as e:
            print(e)
            print("This is a parsing error. Strings in json must be delimited with \" instead of ' ")
            raise PlayListImportErrorException()

        #Verify that some data exists
        for elem in ["blocks","resources"]:
            if not elem in playListStruct:
                print(elem + " not found")
                raise PlayListImportErrorException()


        #Parse the resources
        for resource in playListStruct['resources']:
            if not 'file' in playListStruct['resources'][resource]:
                print("CRITICAL: Resource "+ str(resource) +" has no file attribute");
                raise PlayListImportErrorException()

            if not 'file' in playListStruct['resources'][resource]:
                print("CRITICAL: Resource "+ resource +" does not have a file attribute!")
                raise PlayListImportErrorException()

            if not os.path.exists(playListStruct['resources'][resource]['file']):
                print("CRITICAL: Resource " + str(resource) + " file ("+ playListStruct['resources'][resource]['file'] +") does not exists")
                raise PlayListImportErrorException()



        for dateBlock in playListStruct["blocks"]:

            prev_block_id = 0

            for timeBlock in playListStruct["blocks"][dateBlock]:
                blockStruct = playListStruct["blocks"][dateBlock][timeBlock]

                if len(blockStruct['parts']) == 0:
                    print("WARNING: Skipping block " + str(timeBlock) + " on " + str(dateBlock) + ". No parts to play")
                    continue

                for item in ['name','description', 'parts']:
                    if not item in blockStruct:
                        print ("CRITICAL: Block " + timeBlock +" on " + dateBlock +" does not have a " + item + "!")
                        raise PlayListImportErrorException()


                #blockid is date with seconds, move to unix timestamp
                blockId = ((int(dateBlock) * 10000) + int(timeBlock)) * 100
                blockId = datetime.datetime.strptime(str(blockId), "%Y%m%d%H%M%S")
                blockId = int(time.mktime(blockId.timetuple()))

                block = self.__createBlock(blockId,dateBlock,timeBlock,blockStruct["name"],blockStruct["description"])
                for part in blockStruct['parts']:

                    if not part in playListStruct['resources']:
                        print("CRITICAL: Part " + str(part) + " has no resource file!")
                        raise PlayListImportErrorException()

                    resource = playListStruct['resources'][part]
                    part = self.__createPart(resource)

                    part['playAt'] = blockId + block['totalRunTime']
                    block['parts'].append(part)
                    block['totalRunTime'] += part['duration']

                if prev_block_id > blockId:
                    print("Critical: Block duration overlapping at " + str(blockId))
                    raise PlayListImportErrorException()

                self._playList.append(blockId)
                self._blocks[blockId] = block

        print ("INFO: Loaded " + str(len(self._playList)) + " blocks.")
        self._playList.sort()

    def getCurrentBlock(self):
        curTimeId = int(time.time())
        curBlock = None

        for blockId in self._playList:
            if blockId < curTimeId:
                curBlock = blockId
                continue

            if not curBlock:
                curBlock = blockId
            return self._blocks[curBlock]
        return None

if __name__ == "__main__":
    print "##### DEBUG ######"
    import mkvutils
    m = mkvutils.MkvUtils()
    p = PlayList(m)
    p.load('../cfg/playlist.json')
    print "get", p.getCurrentBlock()
