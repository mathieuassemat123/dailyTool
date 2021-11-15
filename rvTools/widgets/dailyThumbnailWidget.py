from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools
import os

RVTOOLS_PATH =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
THUMBNAIL_UI_PATH = os.path.join(RVTOOLS_PATH, "ui", "itemC.ui")


cloud=os.path.join(RVTOOLS_PATH, "resources", "cloud.png")

class QDailyThumbnailWidget(QtWidgets.QWidget):
    def __init__ (self, parent = None):
        super(QDailyThumbnailWidget, self).__init__(parent)
        uiFile = QtCore.QFile(THUMBNAIL_UI_PATH)
        uiFile.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(uiFile, self)
        self.setColor("darkGray")
        self.pixmapB = None
        self.ui.iconQLabel.setScaledContents(True)
        self.ui.pathLabel.hide()
        image = QtGui.QImage()
        image.load(cloud)
        self.pixmap = QtGui.QPixmap(image)
        self.ui.overlay.setPixmap(cloud)
        self.ui.overlay.setScaledContents(True)
        self.onServer = False

    def setOnServer(self):
    	self.ui.overlay.hide()
        self.onServer = True

    def setTextUp (self, text):
        self.ui.textUpQLabel.setText(text)

    def setTextDown (self, text):
        self.ui.textDownQLabel.setText(text)

    def setVersion (self, text):
        self.ui.versionLabel.setText(text)

    def setDisc (self, text):
        self.ui.discLabel.setText(text)

    def setDate (self, text):
        self.ui.dateLabel.setText(text)

    def setFrameRange (self, text):
        self.ui.frameRangeLabel.setText(text)

    def setStatus (self, text):
        self.ui.statusLabel.setText(text)

    def setMoviePath(self, path):
        self.ui.pathLabel.setText(path)

    def setColor(self, color):
        self.setStyleSheet("background-color: #404040;color: white; border-radius: 7px")

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.ui.setFixedSize(self.size()  - QtCore.QSize(10,10))
        self.ui.frame.setFixedSize(self.size() - QtCore.QSize(20,20) )
        self.ui.frame.setGeometry(QtCore.QRect(5,5,self.size().height(),self.size().width()))

        self.ui.overlay.setGeometry(QtCore.QRect(self.size().width()-40 ,30,20, 20))

        size = self.size() - QtCore.QSize(20,20)
        if size.height() < 150:
            self.ui.dateWidget.hide()
            self.ui.shotWidget.hide()
            self.ui.discWidget.hide()
            self.ui.statWidget.hide()
            self.ui.overlay.hide()
        else :
            self.ui.dateWidget.show()
            self.ui.shotWidget.show()
            self.ui.discWidget.show()
            self.ui.statWidget.show()
            if not self.onServer == True:
            	self.ui.overlay.show()
        if self.pixmapB == None :
            self.pixmapB = self.ui.iconQLabel.pixmap()
        if self.pixmapB :
            pixmapSize = self.pixmapB.size()
            aspectRatio = float(pixmapSize.height()) / float(pixmapSize.width())
            height = (self.size().height() - 25)
            width = int((self.size().width() - 25) * aspectRatio)
            self.ui.iconQLabel.setFixedSize(QtCore.QSize(height,width))


    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass