import sys
from PyQt5.QtWidgets import (
    QTabWidget,
    QMainWindow, QApplication,
    QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider
)
from PyQt5.QtCore import Qt
from UI.Tab1 import Tab1
from UI.Tab2 import Tab2
from UI.Tab3 import Tab3

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("FIH-Tuning")

        self.tabWidget = QTabWidget()

        self.tab1 = Tab1()
        self.tab2 = Tab2()
        self.tab3 = Tab3()

        self.tabWidget.addTab(self.tab1, "選擇project")
        self.tabWidget.addTab(self.tab2, "參數設定")
        self.tabWidget.addTab(self.tab3, "執行")

        self.setCentralWidget(self.tabWidget)

        self.setStyleSheet(
            """
            * {
                background-color: rgb(124, 124, 124);
            }
            
            QMessageBox QLabel {
                font-size:12pt; font-family:微軟正黑體; color:white;
            }

            QMessageBox QPushButton{
                font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);
            }
            """

        )
