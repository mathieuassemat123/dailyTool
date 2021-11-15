from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import sys
import os
import shotgun_api3
import urllib3
from datetime import datetime
import tempfile

RVTOOLS_PATH =   os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DAILIES_UI_PATH = os.path.join(RVTOOLS_PATH, "ui", "dailies.ui")

print DAILIES_UI_PATH

sys.path.append(RVTOOLS_PATH)

import rvTools.trackerRequests.sgRequest as dbRequest
import rvTools.widgets.dailyThumbnailWidget as dailyThumbnailWidget
import rvTools.widgets.thumbnailsGridWidget as thumbnailsGridWidget
import rvTools.tools.thumbnailThread as thumbnailThread

TEMP_FOLDER = tempfile.gettempdir()

STANDALONE = True
import rvTools.playerCommands.rvControl as playerControl
STANDALONE = False





class DailiesPanel (QtWidgets.QMainWindow):
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

    def connectUI(self):
        self.ui.projectsCombo.currentIndexChanged.connect(self.pojectChanged)
        self.ui.projectsCombo.setEditable(True)
        self.ui.projectsCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.ui.projectsCombo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

        self.ui.treeWidget.selectionModel().selectionChanged.connect(self.shotChanged)
        self.ui.playlistTreeWidget.selectionModel().selectionChanged.connect(self.playlistChanged)
        self.ui.dateTreeWidget.selectionModel().selectionChanged.connect(self.dateChanged)


        self.dailiesWidget.myQListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dailiesWidget.myQListWidget.customContextMenuRequested.connect(self.activateContextMenu)
        self.createContextMenu()

    def activateContextMenu(self, point):
        self.dailesContextMenu.exec_(self.dailiesWidget.myQListWidget.mapToGlobal(point))


    def addLayout(self):
        self.dailiesWidget = thumbnailsGridWidget.QthumbnailsGridWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.dailiesWidget)
        self.ui.dailiesWidget.setLayout(layout)


    def populateProjects(self):
        self.ui.projectsCombo.clear()
        self.ui.projectsCombo.addItems(sorted(dbRequest.getProjectsNames()))

    def getSelectedProject(self):
        return str(self.ui.projectsCombo.currentText())


    def pojectChanged(self):
        #self.populateDates()
        self.populateSceneShot()
        self.populatePlaylists()



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
        projectName = self.getSelectedProject()
        playlists = dbRequest.getProjectPlaylists(projectName)
        self.ui.playlistTreeWidget.clear()
        if playlists:
            for playlist in playlists :
                playTree = QtWidgets.QTreeWidgetItem(self.ui.playlistTreeWidget)
                playTree.setText(0, playlist)


    def populateDates(self):
        projectName = self.getSelectedProject()
        dailyDetails = dbRequest.getDailiesDetailsPerDate(projectName)
        self.ui.dateTreeWidget.clear()
        self.dailiesPerDate = dict()
        currentDate = None
        for daily in dailyDetails :
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



    def populateShotWidget(self, sceneName, shotName):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        projectName = self.getSelectedProject()
        if not shotName :
            dailiesDicts = dbRequest.getDailiesDetailsPerScene(projectName, sceneName)
        else :
            dailiesDicts = dbRequest.getDailiesDetailsPerSceneShot(projectName, sceneName, shotName)
        print(dailiesDicts)
        if dailiesDicts :
            for dailyDict in sorted(dailiesDicts, reverse=True):  
                dailyWidget = self.populateDailiesWidget(dailyDict, sceneName, shotName)
                currentQtDailyDict = dict()
                for key in dailyDict.keys():
                    currentQtDailyDict[key] = dailyDict[key]
                self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()


        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())

    

    def populateDateWidget(self, date):
        self.dailiesDict = dict()
        self.dailiesWidget.myQListWidget.clear()
        #self.dailiesPerDate
        for dailyDict in self.dailiesPerDate[date.split(' ')[0]]:  
            dailyWidget = self.populateDailiesWidget(dailyDict, '', '')
            currentQtDailyDict = dict()
            for key in dailyDict.keys():
                currentQtDailyDict[key] = dailyDict[key]
            self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(self.dailiesPerDate[date.split(' ')[0]]))
            self.setIcons()


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
                for key in dailyDict.keys():
                    currentQtDailyDict[key] = dailyDict[key]
                self.dailiesDict[dailyWidget] = currentQtDailyDict
            self.dailiesWidget.countLabel.setText('(%i Dailies)' % len(dailiesDicts))
            self.setIcons()


        self.dailiesWidget.myQListWidget.itemDoubleClicked.connect(self.play)
        self.dailiesWidget.myQListWidget.setGridSize(self.dailiesWidget.myQListWidget.gridSize())




    def setIcons (self):
        if self.thumbnailThread:
            if self.thumbnailThread.isRunning() :
                print('stopping thread')
                self.thumbnailThread.terminate()


        self.thumbnailThread = thumbnailThread.ThumbnailThread(self.dailiesDict)
        self.thumbnailThread.thumbnail.connect(self.setPixmap,QtCore.Qt.QueuedConnection)
        self.thumbnailThread.done.connect(self.thumbnailThread.quit)

        self.thumbnailThread.start()  

        
    def setPixmap(self, pixmap, widgetObject):
        try :
            self.pixmap = pixmap
            widgetObject.ui.iconQLabel.setPixmap(self.pixmap.scaled(4096,4096, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            widgetObject.ui.iconQLabel.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
            pixmapSize = self.pixmap.size()
            aspectRatio = float(pixmapSize.height()) / float(pixmapSize.width())
            height = (widgetObject.size().height() - 25)
            width = int((widgetObject.size().width() - 25) * aspectRatio)
            widgetObject.ui.iconQLabel.setFixedSize(QtCore.QSize(height,width))
        except :
            pass



    def populateDailiesWidget(self, dailyDict, sceneName, shotName):
        if dailyDict :
            thumbnailWidget = dailyThumbnailWidget.QDailyThumbnailWidget()


            thumbnailWidget.setTextUp('%s/%s' % (dailyDict['scene'], dailyDict['shot']))
            thumbnailWidget.setTextDown(dailyDict['user'])
            thumbnailWidget.setVersion('%s' % dailyDict['id'])
            thumbnailWidget.setDisc(dailyDict['department'])
            thumbnailWidget.setDate(dailyDict['date'].strftime("%d-%m-%Y %H:%M"))
            thumbnailWidget.setFrameRange(dailyDict['framerange'])
            thumbnailWidget.setStatus('')
            try :
                thumbnailWidget.setMoviePath(dailyDict['movie'])
                if dailyDict['onServer'] == True :
                    thumbnailWidget.setOnServer()
            except :
                pass

        myQListWidgetItem = QtWidgets.QListWidgetItem(self.dailiesWidget.myQListWidget)
        myQListWidgetItem.setSizeHint(QtCore.QSize(1000,1000))

        self.dailiesWidget.myQListWidget.addItem(myQListWidgetItem)
        self.dailiesWidget.myQListWidget.setItemWidget(myQListWidgetItem, thumbnailWidget)

        return thumbnailWidget


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

    def play(self, item=None):
        if not item :
            item =  self.dailiesWidget.myQListWidget.selectedItems()[0]
        widget = self.dailiesWidget.myQListWidget.itemWidget(item)
        path = self.dailiesDict[widget]['movie']

        if not STANDALONE:
            playerControl.playSingleMedia(path)

    def playAsLayout(self, items):
        print('layout')
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsLayout(allPaths)

    def playAsSequence(self, items):
        print('layout')
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsSequence(allPaths)


    def playAsCompare(self, items):
        print('layout')
        items = self.dailiesWidget.myQListWidget.selectedItems()
        allPaths = []
        for item in items:
            widget = self.dailiesWidget.myQListWidget.itemWidget(item)
            path = self.dailiesDict[widget]['movie']
            allPaths.append(path)

        if not STANDALONE:
            playerControl.playAsCompare(allPaths)