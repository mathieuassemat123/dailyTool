import sys
sys.path.append(r"c:\mytools")
import rvTools.widgets.dailyPanelWidget as dailyPanelWidget
from PySide2 import QtWidgets, QtCore, QtGui, QtUiTools


app = QtWidgets.QApplication([])
window = dailyPanelWidget.DailiesPanel()
window.show()
sys.exit(app.exec_())
