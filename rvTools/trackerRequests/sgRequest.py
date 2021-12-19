import shotgun_api3
import os
from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools



from pymu import MuSymbol
import rv

def defaultSession() :
    rv.runtime.eval ("require slutils;", [])
    (lastSession,sessions) = MuSymbol('slutils.retrieveSessionsData')()
    stuff = lastSession.split('|')
    # return (url, login, token)
    return (stuff[0], stuff[1], stuff[2])


defaultSession = defaultSession()

shotgun =  shotgun_api3.Shotgun(defaultSession[0],
                             session_token=defaultSession[2])






def getProjectsNames():
    projectNames = []
    sgProjects = shotgun.find("Project", [], ['name']) 
    for sgProject in sgProjects :
        projectNames.append(sgProject['name'])
    return projectNames


def getProjectSceneShotsDictionnary(projectName):
    sceneShotDictionnary = dict()
    sgSequences = shotgun.find("Sequence", [['project.Project.name', 'is', projectName]], ['code'])
    if sgSequences:
        for sgSequence in sgSequences:
            sceneShotDictionnary[sgSequence['code']] = []
            filters = [
                ['project.Project.name', 'is', projectName],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': sgSequence['id']}]
            ]
            sgShots = shotgun.find("Shot",filters,['code'])
            for sgShot in sgShots :
                sceneShotDictionnary[sgSequence['code']].append(sgShot['code'])
        return sceneShotDictionnary
    else :
        return None

def getProjectPlaylists(projectName):
    playlistNames = []
    sgPlaylists = shotgun.find("Playlist", [['project.Project.name', 'is', projectName]], ['code'])
    if sgPlaylists:
        for sgPlaylist in sgPlaylists:
            playlistNames.append(sgPlaylist['code'])
        return playlistNames
    else :
        return None

def getProjectAssets(projectName):
    assetNames = []
    sgAssets = shotgun.find("Asset", [['project.Project.name', 'is', projectName]], ['code'])
    if sgAssets:
        for sgAsset in sgAssets:
            assetNames.append(sgAsset['code'])
        return assetNames
    else :
        return None


def _getVersionFields():
    return ['code', 
            'sg_department',
            'created_at',
            'sg_uploaded_movie_image',
            'entity',
            'sg_movie_aspect_ratio',
            'sg_uploaded_movie_webm',
            'updated_at',
            'frame_range',
            'filmstrip_image',
            'created_by',
            'sg_uploaded_movie',
            'sg_path_to_frames',
            'sg_uploaded_movie_mp4',
            'user',
            'image',
            'sg_path_to_movie',
            'id']




def getDailiesDetailsPerScene(projectName, scene):
    dailiesPerScene = _getVersionsPerScene(projectName, scene)
    dailiesDicts = []
    for daily in dailiesPerScene :
        dailiesDicts.append(_convertVersionToDictionnary(daily, scene))
    return dailiesDicts
     

def getDailiesDetailsPerSceneShot(projectName, scene, shot):
    dailiesPerSceneShot = _getVersionsPerSceneShot(projectName, scene, shot)
    dailiesDicts = []
    for daily in dailiesPerSceneShot :
        dailiesDicts.append(_convertVersionToDictionnary(daily, scene))
    return dailiesDicts
    
def getDailiesDetailsPerAsset(projectName, asset):
    dailiesPerSceneShot = _getVersionsPerAsset(projectName, asset)
    dailiesDicts = []
    for daily in dailiesPerSceneShot :
        dailiesDicts.append(_convertVersionToDictionnary(daily, ''))
    return dailiesDicts

def getDailiesDetailsPerDate(projectName):
    dailiesPerDate = _getVersionsPerDate(projectName )
    dailiesDicts = []
    for daily in dailiesPerDate :
        dailiesDicts.append(_convertVersionToDictionnary(daily, 'unknown'))
    return dailiesDicts

def getDailiesDetailsPerSearch(projectName, searchField):
    dailiesPerSearch = _getVersionsPerSearch(projectName, searchField)
    dailiesDicts = []
    for daily in dailiesPerSearch :
        dailiesDicts.append(_convertVersionToDictionnary(daily, 'unknown'))
    return dailiesDicts

def getDailiesDetailsPerPlaylist(projectName, playlist):
    dailiesPerPalylist = _getVersionsPerPlaylist(projectName, playlist)
    dailiesDicts = []
    for daily in dailiesPerPalylist :
        dailiesDicts.append(_convertPlaylistVersionToDictionnary(daily, 'unknown'))
    return dailiesDicts

def _getVersionsPerScene(projectName, scene):
    sgVersions = None
    sgSequences = shotgun.find("Sequence", [['project.Project.name', 'is', projectName]], ['code'])
    for sgSequence in sgSequences :
        if sgSequence['code'] == scene :
            filters =     [
                        ['project.Project.name', 'is', projectName],
                        ['entity', 'name_contains', scene]
                           ]
            fields = _getVersionFields()
            sgVersions = shotgun.find("Version",filters, fields)
            break
    if sgVersions :
        return sgVersions
    else :
        return []
        
        
def _getVersionsPerSearch(projectName, searchField):
    sgVersions = []
    filters =     [
                ['project.Project.name', 'is', projectName],
                ['user', 'name_contains', searchField]
                   ]
    fields = _getVersionFields()
    sgVersions = shotgun.find("Version",filters, fields)
    if sgVersions :
        return sgVersions
    else :
        return []



def _getVersionsPerPlaylist(projectName, playlist):
    sgVersions = None
    sgSequences = shotgun.find("Playlist", [['project.Project.name', 'is', projectName]], ['code'])
    for sgSequence in sgSequences :
       
        if sgSequence['code'] == playlist:

        
            filters = [['playlist', 'is', {'type':'Playlist', 'id':sgSequence['id']}]]
            originalFields =_getVersionFields()
            fields = []
            for field in originalFields :
                fields.append('version.Version.%s'%field)

            sgVersions = shotgun.find('PlaylistVersionConnection', filters, fields)
            return sgVersions


        
def _getVersionsPerAsset(projectName, asset):
    sgVersions = None
    sgSequences = shotgun.find("Asset", [['project.Project.name', 'is', projectName]], ['code'])
    for sgSequence in sgSequences :
        if sgSequence['code'] == asset :
            filters = [
                ['project.Project.name', 'is', projectName],
                ['entity', 'is', {'type': 'Asset', 'id': sgSequence['id']}]
                    ]

            fields = _getVersionFields()
            sgVersions = shotgun.find("Version",filters, fields)
            break
    if sgVersions :
        return sgVersions
    else :
        return []


def _getVersionsPerSceneShot(projectName, scene, shot):
    sgSequences = shotgun.find("Sequence", [['project.Project.name', 'is', projectName]], ['code'])
    for sgSequence in sgSequences :
        if sgSequence['code'] == scene :
            filters = [
                ['project.Project.name', 'is', projectName],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': sgSequence['id']}]
            ]
            sgShots= shotgun.find("Shot",filters,['code'])
            for sgShot in sgShots :
                if sgShot['code'] == shot :
                    filters =     [
                                ['project.Project.name', 'is', projectName],
                                ['entity', 'is', {'type': 'Shot', 'id': sgShot['id']}]
                                ]
                    fields = _getVersionFields()
                    sgVersions = shotgun.find("Version",filters, fields)
            break
    if sgVersions :
        return sgVersions
    else :
        return []

def _getVersionsPerDate(projectName):
    fields = _getVersionFields()
    filters = [
    ['project.Project.name', 'is', projectName],
    ]
    sgVersions = shotgun.find("Version",filters, fields)
    sortedbyDate =  sorted(sgVersions, key=lambda k: k['created_at'], reverse=True)
    return sortedbyDate




def _convertVersionToDictionnary(sgVersion, scene):
    if sgVersion :
        try :
            dailyDetails = dict()
            dailyDetails['image'] = sgVersion['image']
            dailyDetails['filmstrip_image'] = sgVersion['filmstrip_image']
            dailyDetails['department'] = dailyDetails['id'] = sgVersion['code'].split('_')[-2] 
            #sgVersion['sg_department']
            #dailyDetails['id'] = sgVersion['id']
            dailyDetails['version'] = sgVersion['code'].split('_')[-1]
            dailyDetails['id'] = sgVersion['id']

            dailyDetails['date'] = sgVersion['created_at']
            dailyDetails['user'] = sgVersion['user']['name']
            dailyDetails['shot'] = sgVersion['entity']['name']
            dailyDetails['scene'] = scene
            dailyDetails['framerange'] = sgVersion['frame_range']
            dailyDetails['source'] = sgVersion['sg_path_to_frames']
            if sgVersion['sg_path_to_movie'] and os.path.isfile( sgVersion['sg_path_to_movie']):
                dailyDetails['movie'] = sgVersion['sg_path_to_movie']
                dailyDetails['onServer'] = True
            else :
                try :
                    dailyDetails['movie'] = sgVersion['sg_uploaded_movie']['url']
                    dailyDetails['onServer'] = False
                except :
                    pass


            return dailyDetails
        except :
            pass




def _convertPlaylistVersionToDictionnary(sgVersion, scene):
    if sgVersion :
       # try :
            dailyDetails = dict()
            dailyDetails['image'] = sgVersion['version.Version.image']
            dailyDetails['filmstrip_image'] = sgVersion['version.Version.filmstrip_image']
            dailyDetails['department'] = dailyDetails['id'] = sgVersion['version.Version.code'].split('_')[-2] 
            #sgVersion['sg_department']
            dailyDetails['id'] = sgVersion['version.Version.id']
            dailyDetails['version'] = sgVersion['version.Version.code'].split('_')[-1]
            dailyDetails['date'] = sgVersion['version.Version.created_at']
            dailyDetails['user'] = sgVersion['version.Version.user']['name']
            dailyDetails['shot'] = sgVersion['version.Version.entity']['name']
            dailyDetails['scene'] = scene
            dailyDetails['framerange'] = sgVersion['version.Version.frame_range']

            if sgVersion['version.Version.sg_path_to_movie'] and os.path.isfile( sgVersion['version.Version.sg_path_to_movie']):
                dailyDetails['movie'] = sgVersion['version.Version.sg_path_to_movie']
                dailyDetails['onServer'] = True
            else :
                try :
                    dailyDetails['movie'] = sgVersion['version.Version.sg_uploaded_movie']['url']
                    dailyDetails['onServer'] = False
                except :
                    pass

            return dailyDetails

        #except :
        #    pass


#dailyDetails['movie'] = str(defaultSession[0]) + '/file_serve/version/' + str(sgVersion['id']) + '/mp4'



