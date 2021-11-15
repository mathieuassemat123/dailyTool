from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools


class TumbnailsListWidget(QtWidgets.QListWidget):
    def __init__(self, parent = None):
        super(TumbnailsListWidget, self).__init__(parent)


    def wheelEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            newSize = self.gridSize() + QtCore.QSize(int(event.angleDelta().y()/20),int(event.angleDelta().y()/20))
            if newSize.height() > 50 and newSize.height() < 800 :
                self.setGridSize(newSize)
        else :
            QtWidgets.QListWidget.wheelEvent(self, event)

    def resizeEvent(self, event):
        QtWidgets.QListWidget.resizeEvent(self, event)
        self.setGridSize(self.gridSize())

    def startDrag(self, supportedActions):
        drag = QtGui.QDrag(self)
        for item in self.selectedItems():
            print(item.__class__.__name__)
        link = (self.itemWidget(item).ui.pathLabel.text())

        mimeData = self.model().mimeData(self.selectedIndexes())
        mimeData.setText(self.itemWidget(item).ui.versionLabel.text().replace('id', '').replace('v', ''))
        mimeData.setUrls([QtCore.QUrl.fromLocalFile(str(link))])
        drag.setMimeData(mimeData)
        if drag.start(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            for item in self.selectedItems():
                self.takeItem(self.row(item))


class QthumbnailsGridWidget(QtWidgets.QWidget):
    def __init__ (self):
        super(QthumbnailsGridWidget, self).__init__()
        # Create QListWidget
        self.countLabel = QtWidgets.QLabel()
        self.countLabel.setAlignment(QtCore.Qt.AlignCenter)
        myFont=QtGui.QFont()
        myFont.setBold(True)
        self.countLabel.setFont(myFont)
        self.myQListWidget = TumbnailsListWidget()
        self.myQListWidget.setFlow(QtWidgets.QListWidget.LeftToRight)
        #self.myQListWidget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.myQListWidget.setSpacing(5)
        self.myQListWidget.setGridSize(QtCore.QSize(230,230))
        self.myQListWidget.setViewMode(QtWidgets.QListWidget.IconMode)
        self.myQListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        #self.myQListWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.countLabel)

        layout.addWidget(self.myQListWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.myQListWidget.itemSelectionChanged.connect(self.selectionListChanged)



    def resetColors(self):
        children = self.myQListWidget.children()
        for child in children :
            for secondChild in child.children():
                try:
                    secondChild.setStyleSheet("background-color: #404040; color: white; border-radius: 7px")
                except :
                    pass

    def selectionListChanged(self):
        self.resetColors()
        selectedItems = self.myQListWidget.selectedItems()
        for item in selectedItems :
            widget = self.myQListWidget.itemWidget(item)
            widget.setStyleSheet("background-color: #808080; color: white; border-radius: 7px")