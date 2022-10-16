from PyQt5 import QtCore, QtWidgets, QtGui


from MainWindow import MainWindow

import sys
# 自適應分辨率
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
# 適應windows縮放
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
# 設置支持小數放大比例（適應如125%的縮放比）  
QtGui.QGuiApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)  

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.showMaximized()
sys.exit(app.exec_())