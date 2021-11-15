from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import os
import urllib3

TEMP_FOLDER = r'C:\temp'


class ThumbnailThread(QtCore.QThread):  
    thumbnail = QtCore.Signal(object, object)
    done = QtCore.Signal() #create a custom sygnal we can subscribe to to emit update commands  
    def __init__(self, dailiesDict, parent=None):  
        super(ThumbnailThread,self).__init__(parent)  
        self.exiting = False  
        self.dailiesDict = dailiesDict
  
    def run(self): 
        for widgetObject in self.dailiesDict:
            name = '%s.jpg' % self.dailiesDict[widgetObject]['id']
            image = QtGui.QImage()
            tempFile = os.path.join(TEMP_FOLDER, name)
            if not os.path.isfile(tempFile) :
                http = urllib3.PoolManager()
                urlThumbnail = self.dailiesDict[widgetObject]['image']
                image.loadFromData(http.request('GET', urlThumbnail).data)
                self.pixmap = QtGui.QPixmap(image)
                self.thumbnail.emit(self.pixmap, widgetObject)
                self.done.emit()
                image.save(tempFile)
            else :
                image.load(tempFile)
                self.pixmap = QtGui.QPixmap(image)
                self.thumbnail.emit(self.pixmap, widgetObject)
                self.done.emit()

