import json

from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import os
import urllib3

RVTOOLS_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
UNAIVAILABLE_PATH = os.path.join(RVTOOLS_PATH, "resources", "cloud.png")

f =  open(os.path.join(RVTOOLS_PATH, "config", "config.json"))
TEMP_FOLDER = json.load(f)["thumbnailCacheFolder"] 


class ThumbnailThread(QtCore.QObject):  
    thumbnail = QtCore.Signal(object, object)
    done = QtCore.Signal() #create a custom sygnal we can subscribe to to emit update commands  
    
    def __init__(self, dailiesDict, parent=None):  
        super(ThumbnailThread,self).__init__(parent)  
        self.exiting = False  
        self.dailiesDict = dailiesDict
        
    @QtCore.Slot()
    def fetchTumbnails(self): 
        http = urllib3.PoolManager()
        i = 0
        for widgetObject in self.dailiesDict:
            try :
                i += 1
                name = '%s.jpg' % self.dailiesDict[widgetObject]['id']
                image = QtGui.QImage()
                tempFile = os.path.join(TEMP_FOLDER, name)
                thumbfile = self.dailiesDict[widgetObject]['image']
                
                #if not os.path.isfile(thumbfile) :
                #    thumbfile = self.dailiesDict[widgetObject]['filmstrip_image']
                if not thumbfile.count('thumbnail_pending'):
                    if not os.path.isfile(tempFile) :
                        urlThumbnail = thumbfile
                        image.loadFromData(http.request('GET', urlThumbnail).data)
                        self.pixmap = QtGui.QPixmap(image)
                        self.thumbnail.emit(self.pixmap, widgetObject)
                        #print urlThumbnail
                        try :
                            image.save(tempFile)
                        except : 
                            pass

                    else :
                        image.load(tempFile)
                        self.pixmap = QtGui.QPixmap(image)
                        self.thumbnail.emit(self.pixmap, widgetObject)
            except :
                image = QtGui.QImage()
                image.load(UNAIVAILABLE_PATH)
                self.pixmap = QtGui.QPixmap(image)
                self.thumbnail.emit(self.pixmap, widgetObject)
        self.done.emit()

