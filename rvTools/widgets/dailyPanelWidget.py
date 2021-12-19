from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import sys
import os
import shotgun_api3
import urllib3
from datetime import datetime
import tempfile

RVTOOLS_PATH =   os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DAILIES_UI_PATH = os.path.join(RVTOOLS_PATH, "ui", "dailies.ui")

sys.path.append(RVTOOLS_PATH)

import rvTools.trackerRequests.sgRequest as dbRequest
import rvTools.widgets.dailyThumbnailWidget as dailyThumbnailWidget
import rvTools.widgets.thumbnailsGridWidget as thumbnailsGridWidget
import rvTools.tools.thumbnailThread as thumbnailThread

TEMP_FOLDER = tempfile.gettempdir()

import rvTools.playerCommands.rvControl as playerControl
STANDALONE = False
from functools import partial




class DailiesPanel (QtWidgets.QMainWindow):
    '''
    Main class for the RV widget
    '''
    
    def __init__ (self):
        super(DailiesPanel, self).__init__()
        uiFile = QtCore.QFile(DAILIES_UI_PATH)
        uiFile.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(uiFile, self)
        self.addLayout()
        self.populateProjects()
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.treeWidget.sortByColumn(0,  QtCore.Qt.AscendingOrder)
        self.thumbnailThread = None
        self.connectUI()
        self.dictPixmapsToFetch = dict()
        QtGui.QPixmapCache.setCacheLimit(999999)
        

    def connectUI(self):
        '''
        Connect UI elements
        '''
        self.ui.projectsCombo.currentIndexChanged.connect(self.pojectChanged)
        self.ui.projectsCombo.setEditable(True)
        self.ui.projectsCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.ui.projectsCombo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        self.ui.treeWidget.selectionModel().selectionChanged.connect(self.shotChanged)
        self.ui.playlistTreeWidget.selectionModel().selectionChanged.connect(self.playlistChanged)
        self.ui.dateTreeWidget.selectionModel().selectionChanged.connect(self.dateChanged)
        self.ui.assetTreeWidget.selectionModel().selectionChanged.connect(self.assetChanged)


        self.dailiesWidget.myQListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dailiesWidget.myQListWidget.customContextMenuRequested.connect(self.activateContextMenu)
        self.createContextMenu()
        
        self.ui.searchButton.clicked.connect(self.populateSearchWidget)
        self.ui.searchLineEdit.returnPressed.connect(self.populateSearchWidget)
        self.ui.tabWidget.currentChanged.connect(self.tabChanged)

    def activateContextMenu(self, point):
        self.dailesContextMenu.exec_(self.dailiesWidget.myQListWidget.mapToGlobal(point))


    def addLayout(self):
        '''
        create the dailies thumbnail grid widget
        '''
        
        self.dailiesWidget = thumbnailsGridWidget.QthumbnailsGridWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.dailiesWidget)
        self.ui.dailiesWidget.setLayout(layout)


    def populateProjects(self):
        '''
        populate projects from shotgrid database
        '''
        
        self.ui.projectsCombo.clear()
        self.ui.projectsCombo.addItems(sorted(dbRequest.getProjectsNames()))

    def getSelectedProject(self):
        '''
        return current project
        '''
        return str(self.ui.projectsCombo.currentText())


    def pojectChanged(self):
        self.populateSceneShot()
        self.populatePlaylists()
        self.populateAssets()

    def tabChanged(self):
        print self.ui.tabWidget.currentIndex
        if self.ui.tabWidget.currentIndex() == 2 :
            self.populateDates()

            

    def populateSceneShot(self):
        projectName = self.getSelectedProject()
        sceneShots = dbRequest.getProjectSceneShotsDictionnary(projectName)
        self.ui.treeWidget.clear()
        if sceneShots:
            for scene in sceneShots.keys() :
                seqTree = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
                seqTree.setText(0, scene)
                for shot in sceneShots[scene] :
                    shotTree = QtWidgets.QTreeWidgetItem(seqTree)
                    shotTree.setText(0, shot)  


    def populatePlaylists(self):
        '''
        populate playlist list
        '''
        projectName = self.getSelectedProject()
        playlists = dbRequest.getProjectPlaylists(projectName)
        self.ui.playlistTreeWidget.clear()
        if playlists:
            for playlist in playlists :
                playTree = QtWidgets.QTreeWidgetItem(self.ui.playlistTreeWidget)
                playTree.setText(0, playlist)

    def populateAssets(self):
        '''
        populate assets list
        '''
        projectName = self.getSelectedProject()
        assets = dbRequest.getProjectAssets(projectName)
        self.ui.assetTreeWidget.clear()
        if assets:
            for asset in assets :
                playTree = QtWidgets.QTreeWidgetItem(self.ui.assetTreeWidget)
                playTree.setText(0, asset)


    def populateDates(self):
        '''
        populate date list
        Dangerously slow to query on shotgun, will need some caching
        '''
        
        projectName = self.getSelectedProject()
        dailyDetails = dbRequest.getDailiesDetailsPerDate(projectName)
        self.ui.dateTreeWidget.clear()
        self.dailiesPerDate = dict()
        currentDate = None
        for daily in sorted(dailyDetails, reverse = True) :
            if  daily :
                if daily['date'].strftime("%d-%m-%Y") != currentDate :
                    currentDate = daily['date'].strftime("%d-%m-%Y")
                    self.dailiesPerDate[currentDate] = [daily]
                else :
                    self.dailiesPerDate[currentDate].append(daily)

        for date in self.dailiesPerDate :
            dateTree = QtWidgets.QTreeWidgetItem(self.ui.dateTreeWidget)
            dateTree.setText(0, '%s (%i Dailies)' % (date, len(self.dailiesPerDate[date])))



    def shotChanged(self):
        treeWidgetItem = self.ui.treeWidget.selectedItems()
        if treeWidgetItem :
            if treeWidgetItem[0].parent():
                shot = treeWidgetItem[0].text(0)
                scene = treeWidgetItem[0].parent().text(0)
            else :
                scene = treeWidgetItem[0].text(0)
                shot = None

            self.populateShotWidget(scene, shot)


    def dateChanged(self):
        treeWidgetItem = self.ui.dateTreeWidget.selectedItems()
        if treeWidgetItem :
            date = treeWidgetItem[0].text(0)
            self.populateDateWidget(date)

    def playlistChanged(self):
        treeWidgetItem = self.ui.playlistTreeWidget.selectedItems()
        if treeWidgetItem :
            playlist = treeWidgetItem[0].text(0)
            self.populatePlaylistWidget(playlist)

    def assetChanged(self):
        treeWidgetItem = self.ui.assetTreeWidget.selectedItems()
        if treeWidgetItem :
            asset = treeWidgetItem[0].text(0)
            self.populateAssetWidget(asset)

    def populateShotWidget(self, sceneName, shotName):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        projectName = self.getSelectedProject()
        if not shotName :
            dailiesDicts = dbRequest.getDailiesDetailsPerScene(projectName, sceneName)
        else :
            dailiesDicts = dbRequest.getDailiesDetailsPerSceneShot(projectName, sceneName, shotName)
        if dailiesDicts :
            for dailyDict in sorted(dailiesDicts, reverse=True):  
                dailyWidget = self.populateDailiesWidget(dailyDict, sceneName, shotName)
                currentQtDailyDict = dict()
                if dailyDict :
                    for key in dailyDict.keys():
                        currentQtDailyDict[key] = dailyDict[key]
                    self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()
        else :
            self.dailiesWidget.countLabel.setText('(0 Dailies)')


        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())

    

    def populateDateWidget(self, date):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        if self.dailiesPerDate:
            for dailyDict in self.dailiesPerDate[date.split(' ')[0]]:  
                dailyWidget = self.populateDailiesWidget(dailyDict, '', '')
                currentQtDailyDict = dict()
                for key in dailyDict.keys():
                    currentQtDailyDict[key] = dailyDict[key]
                self.dailiesDict[dailyWidget] = currentQtDailyDict
                self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(self.dailiesPerDate[date.split(' ')[0]]))
                self.setIcons()
        else :
            self.dailiesWidget.countLabel.setText('(0 Dailies)')

        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())




    def populatePlaylistWidget(self, playlist):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        projectName = self.getSelectedProject()

        dailiesDicts = dbRequest.getDailiesDetailsPerPlaylist(projectName, playlist)
        if dailiesDicts :
            for dailyDict in sorted(dailiesDicts, reverse=True):  
                dailyWidget = self.populateDailiesWidget(dailyDict, '', '')
                currentQtDailyDict = dict()
                if dailyDict :
                    for key in dailyDict.keys():
                        currentQtDailyDict[key] = dailyDict[key]
                    self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()


        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())


    def populateAssetWidget(self, asset):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        projectName = self.getSelectedProject()

        dailiesDicts = dbRequest.getDailiesDetailsPerAsset(projectName, asset)
        if dailiesDicts :
            for dailyDict in sorted(dailiesDicts, reverse=True):  
                dailyWidget = self.populateDailiesWidget(dailyDict, '', '')
                currentQtDailyDict = dict()
                if dailyDict :
                    for key in dailyDict.keys():
                        currentQtDailyDict[key] = dailyDict[key]
                    self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()
        else :
            self.dailiesWidget.countLabel.setText('(0 Dailies)')

        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())


    def setIcons (self):
        '''
        run the thread to gather the dailies thumbnails
        '''
        self.dictPixmapsToFetch = dict()
        key = QtGui.QPixmapCache.Key()
        for widgetObject in sorted(self.dailiesDict, reverse = True):
            thumbnail = self.dailiesDict[widgetObject]['id']
            pix = QtGui.QPixmapCache.find(str(thumbnail))
            if pix == None :
                self.dictPixmapsToFetch[widgetObject] = self.dailiesDict[widgetObject]
            else :
                self.setPixmap(pix, widgetObject, dontAdd=True)
                   
        if self.dictPixmapsToFetch :     
            self.thumbnailThread = QtCore.QThread(self)
            self.thumbnailFetcher = thumbnailThread.ThumbnailThread(self.dictPixmapsToFetch)
            self.thumbnailFetcher.moveToThread(self.thumbnailThread)
            self.thumbnailFetcher.thumbnail.connect(self.setPixmap,QtCore.Qt.QueuedConnection)
            self.thumbnailFetcher.done.connect(self.thumbnailThread.terminate)
            self.thumbnailThread.started.connect(self.thumbnailFetcher.fetchTumbnails)
            self.thumbnailThread.start()  

            
        

    def terminateThread(self):
        '''
        this was just here for debugging purpose
        '''
        pass
        
    def setPixmap(self, pixmap, widgetObject, dontAdd=False):
        '''
        Set daily thumbnail when fetched back from the thread
            pixmap - QPixmap containining the thumbnail
            widgetObject - Dailies thumbnails QWidget
            dontAdd - boolean, if thumbnail already cached in memory. don't add it to the cache
            
            broad exception to remove later, some threading issues are happening
            '''
            
        try :
            self.pixmap = pixmap
            widgetObject.ui.iconQLabel.setPixmap(self.pixmap.scaled(512,512, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            widgetObject.ui.iconQLabel.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
            pixmapSize = self.pixmap.size()
            aspectRatio = float(pixmapSize.height()) / float(pixmapSize.width())
            height = (widgetObject.size().height() - 25)
            width = int((widgetObject.size().width() - 25) * aspectRatio)
            widgetObject.ui.iconQLabel.setFixedSize(QtCore.QSize(height,width))
            if not dontAdd :
                QtGui.QPixmapCache.insert( str(self.dailiesDict[widgetObject]['id']), pixmap)
        except :
            pass


    def populateDailiesWidget(self, dailyDict, sceneName, shotName):
        '''
        populate dailies widget
            dailyDict - dictionnary, Versions and attributes
            sceneName - name of the sequence
            shotName - name of the shot
        '''
        
        if dailyDict :
            thumbnailWidget = dailyThumbnailWidget.QDailyThumbnailWidget()
            thumbnailWidget.setTextUp('%s' % ( dailyDict['shot']))
            thumbnailWidget.setTextDown(dailyDict['user'])
            thumbnailWidget.setVersion('%s' % dailyDict['id'])
            thumbnailWidget.setDisc(dailyDict['department'])
            thumbnailWidget.setDate(dailyDict['date'].strftime("%d-%m-%Y %H:%M"))
            thumbnailWidget.setFrameRange(dailyDict['framerange'])
            thumbnailWidget.setStatus('')
            try :
                thumbnailWidget.setMoviePath(dailyDict['movie'])
                if dailyDict['onServer'] == True :
                    #means version not available on disk, will fetch Wt from the weblink
                    thumbnailWidget.setOnServer()
            except :
                pass


            myQListWidgetItem = QtWidgets.QListWidgetItem(self.dailiesWidget.myQListWidget)
            myQListWidgetItem.setSizeHint(QtCore.QSize(1000,1000))

            self.dailiesWidget.myQListWidget.addItem(myQListWidgetItem)
            self.dailiesWidget.myQListWidget.setItemWidget(myQListWidgetItem, thumbnailWidget)

            return thumbnailWidget
        else :
            return dict()

    def populateSearchWidget(self):
        searchField = self.ui.searchLineEdit.text()
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        projectName = self.getSelectedProject()

        dailiesDicts = dbRequest.getDailiesDetailsPerSearch(projectName, searchField)
        if dailiesDicts :
            for dailyDict in sorted(dailiesDicts, reverse=True):  
                dailyWidget = self.populateDailiesWidget(dailyDict, '', '')
                currentQtDailyDict = dict()
                if dailyDict :
                    for key in dailyDict.keys():
                        currentQtDailyDict[key] = dailyDict[key]
                    self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()


    
    def createContextMenu(self):
        self.dailesContextMenu = QtWidgets.QMenu()

        action = QtWidgets.QAction('Play as Sequence', self)
        self.dailesContextMenu.addAction(action)
        action.triggered.connect(self.playAsSequence)

        action = QtWidgets.QAction('Play as Layout', self)
        self.dailesContextMenu.addAction(action)
        action.triggered.connect(self.playAsLayout)

        action = QtWidgets.QAction('Compare', self)
        self.dailesContextMenu.addAction(action)
        action.triggered.connect(self.playAsCompare)

        action = QtWidgets.QAction('Play source', self)
        self.dailesContextMenu.addAction(action)
        action.triggered.connect(self.playAsSource)


    def play(self, item=None):
        if not item :
            item =  self.dailiesWidget.myQListWidget.selectedItems()[0]
        widget = self.dailiesWidget.myQListWidget.itemWidget(item)
        path = self.dailiesDict[widget]['movie']
        id = self.dailiesDict[widget]['id']

        if not STANDALONE:
            playerControl.playSingleMedia(path, id)
            
            
    def playAsSource(self, item=None):
        if not item :
            item =  self.dailiesWidget.myQListWidget.selectedItems()[0]
        widget = self.dailiesWidget.myQListWidget.itemWidget(item)
        path = self.dailiesDict[widget]['source']

        if not STANDALONE:
            playerControl.playSingleMedia(path)

    def playAsLayout(self, items):
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsLayout(allPaths)

    def playAsSequence(self, items):
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsSequence(allPaths)


    def playAsCompare(self, items):
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsCompare(allPaths)
