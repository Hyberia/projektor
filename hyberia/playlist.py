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
__version__ = "0.4"
__contributors__= "Mathieu Charron, Martin Samson"

import os,sys,datetime,json,logging,time

class PlayListNotFoundException(Exception): pass
class PlayListImportErrorException(Exception): pass
class PlayListFileNotFoundException(Exception): pass
class PlayListVIBNotSetException(Exception): pass

class PlayList():
    def __init__(self, videoInfoBackend = None):
        '''videoInfoBackend Hyberia VIB API compatible backend class instance'''
        # Instanciate the logger
        self.logger = logging.getLogger("hyberia.playlist")

        if videoInfoBackend == None:
            self.logger.critical("HVIB not set")
            raise PlayListVIBNotSetException()

        #Look for HVIB_API_VERSION attr
        try:
            getattr(videoInfoBackend, "HVIB_API_VERSION")
        except AttributeError:
            self.logger.critical("Non-HVIB compliant videoInfoBackend.")
            raise PlayListVIBNotSetException()

        #Verify it matches required version
        if not videoInfoBackend.HVIB_API_VERSION >= 1:
            self.logger.critical("CRITICAL: Incompatible HVIB")
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
        if resource.startswith('#'):
            #The video file name
            part['file'] = resource['file']
            part['name'] = resource['name']
        else:
            part['file'] = resource
            part['name'] = resource

        #Duration in seconds
        part['duration'] = self.__videoInfoBackend.HVIB_RunningTime(part['file'])

        #Will hold when to play the file as a datetime format (yyyymmddhhiiss)
        part['playAt'] = 0
        return part

    def __parsePlayList(self, playListStruct):
        #Verify that some data exists
        for elem in ["blocks","resources"]:
            if not elem in playListStruct:
                self.logger.warning("%s not found." % elem)
                raise PlayListImportErrorException()


        #Parse the resources
        for resource in playListStruct['resources']:
            if not 'file' in playListStruct['resources'][resource]:
                self.logger.critical("Resource %s has no file attribute" % resource);
                raise PlayListImportErrorException()

            if not 'file' in playListStruct['resources'][resource]:
                self.logger.critical("Resource %s does not have a file attribute!" % resource)
                raise PlayListImportErrorException()

            if not os.path.exists(playListStruct['resources'][resource]['file']):
                self.logger.critical("Resource %s file (%s) does not exists" % (resource,playListStruct['resources'][resource]['file']))
                raise PlayListImportErrorException()

        for dateBlock in playListStruct["blocks"]:

            prev_block_id = 0

            for timeBlock in playListStruct["blocks"][dateBlock]:
                blockStruct = playListStruct["blocks"][dateBlock][timeBlock]

                if len(blockStruct['parts']) == 0:
                    self.logger.warning("Skipping block %s on %s. No parts to play", (timeBlock , dateBlock))
                    continue

                for item in ['name','description', 'parts']:
                    if not item in blockStruct:
                        self.logger.critical("Block %s on %s does not have a %s!" %s (timeBlock,dateBlock,item))
                        raise PlayListImportErrorException()

                #blockid is date with seconds, move to unix timestamp
                blockId = ((int(dateBlock) * 10000) + int(timeBlock)) * 100
                blockId = datetime.datetime.strptime(str(blockId), "%Y%m%d%H%M%S")
                blockId = int(time.mktime(blockId.timetuple()))

                block = self.__createBlock(blockId,dateBlock,timeBlock,blockStruct["name"],blockStruct["description"])
                for part in blockStruct['parts']:
                    '''
                    Part can either be:
                        - Resource (identified by starting with a #)
                        - File path.
                    '''
                    if part.startswith('#'):
                        part = part[1:]
                        if not part in playListStruct['resources']:
                            self.logger.critical("Part %s has no resource file!" % part)
                            raise PlayListImportErrorException()

                        resource = playListStruct['resources'][part]['file']
                    else:
                        if not os.path.exists(part):
                            self.logger.critical("Part %s does not exists!" % part)
                            raise PlayListImportErrorException()
                        resource = part

                    part = self.__createPart(resource)

                    part['playAt'] = blockId + block['totalRunTime']
                    block['parts'].append(part)
                    block['totalRunTime'] += part['duration']

                if prev_block_id > blockId:
                    self.logger.critical("Block duration overlapping at %s !" % blockId)
                    raise PlayListImportErrorException()

                self._playList.append(blockId)
                self._blocks[blockId] = block

        self.logger.debug(" Loaded %s blocks." % len(self._playList))


    def __loadCache(self, cacheFile):
        import pickle
        try:
            (p,b) = pickle.load(open(cacheFile,'rb'))
            self._playList = p
            self._blocks = b
        except Exception:
            self.logger.critical("Error: could not load cache file %s" % cacheFile)
            return False
        return True

    def load(self, playListFile, cacheFile = None):
        '''Load a playlist either from file or from cache

        Generating a playlist will take time as mkv information needs to be gathered.
        Using a binary cache speeds up starting Projektor again if no files are missing.
        '''

        if cacheFile != None and os.path.exists(cacheFile):
            if self.__loadCache(cacheFile):
                self.logger.info("Using %s cache file as playlist" % cacheFile)
                return True

        '''Load the playlist file into memory'''
        self.logger.debug("Loading playlist from %s ." % (playListFile,))

        #Verify the playlist file exists
        if not os.path.exists(playListFile):
            self.logger.critical("Playlist file not found.");
            raise PlayListNotFoundException()

        #Attempt to parse the playlist file
        try:
            playListStruct = json.load(open(playListFile, "r"))
        except Exception as e:
            self.logger.warning("This is a parsing error. Strings in json must be delimited with \" instead of ' .")
            self.logger.critical(e)
            raise PlayListImportErrorException()

        self.__parsePlayList(playListStruct)
        self._playList.sort()

        if cacheFile != None:
            try:
                import pickle
                pickle.dump([self._playList, self._blocks], open(cacheFile,'wb'))
            except Exception as e:
                self.logger.warning("Could not save playlist cache.")
            self.logger.info("Playlist saved as %s cache file" % cacheFile)

    def getCurrentBlock(self):
        curTimeId = int(time.time())
        self.logger.debug("Current Timeblock is %i" % (curTimeId,))
        prevBlock = None
        for blockId in self._playList:
            ''' Loop through the blocks to find the one that should be playing
            or will play next

            if the blockId is greater than the curTimeId, it means we either
            have found the currently playing block or the one that will be played.
            '''
            if blockId < curTimeId:
                prevBlock = blockId
                continue
            else:
                '''If the previous block totalruntime is greater than the current time
                return it'''
                if prevBlock and ( self._blocks[prevBlock]['totalRunTime'] + prevBlock ) > curTimeId:
                    return self._blocks[prevBlock]
                else:
                    return self._blocks[blockId]

        ''' We could fall here if we have reached the last playing block'''
        if prevBlock:
            if ( self._blocks[prevBlock]['totalRunTime'] + prevBlock ) > curTimeId:
                return self._blocks[prevBlock]
        return None
