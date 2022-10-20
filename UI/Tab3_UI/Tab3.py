from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTabWidget, QScrollArea
)

from PyQt5 import QtCore
from .UpperPart import UpperPart


class TabPlot(QWidget):
    def __init__(self, name):
        super().__init__()

        plot_wraprt = QVBoxLayout(self)
        self.label_plot = QLabel(name)
        self.label_plot.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label_plot.setAlignment(QtCore.Qt.AlignCenter)
        self.label_plot.setStyleSheet("QLabel{background-color:rgb(0, 0, 0)}")
        plot_wraprt.addWidget(self.label_plot)

class TabInfo(QWidget):
    def __init__(self, name):
        super().__init__()
        HLayout = QHBoxLayout(self)
        self.label = QLabel(name)
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel{background-color:rgb(0, 0, 0)}")

        #Scroll Area Properties
        self.scroll = QScrollArea() 
        # self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.label)

        HLayout.addWidget(self.scroll)


class LowerPart(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tab_info = TabInfo("info")
        self.addTab(self.tab_info, "info")

        self.tab_score = TabPlot("分數圖")
        self.addTab(self.tab_score, "分數圖")

        self.tab_hyper = TabPlot("超參數")
        self.addTab(self.tab_hyper, "超參數")

        self.tab_loss = TabPlot("loss")
        self.addTab(self.tab_loss, "loss")

        self.tab_update = TabPlot("update rate")
        self.addTab(self.tab_update, "update rate")

class Tab3(QWidget):
    def __init__(self, data, config):
        super().__init__()
        self.data = data
        self.config = config
        

        self.setup_UI()
        self.setup_controller()
        
    def setup_UI(self):
        ###### parent ######
        gridLayout = QGridLayout(self)
        ###### parent ######

        ###### Upper Part ###### 
        self.upper_part= UpperPart()
        gridLayout.addWidget(self.upper_part, 0, 0, 1, 1)
        ###### Upper Part ###### 

        ###### Lower Part (plot tab)###### 
        self.lower_part= LowerPart()
        gridLayout.addWidget(self.lower_part, 1, 0, 1, 1)
        ###### Lower Part (plot tab)###### 


        ###### Set Style ###### 
        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                          "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}")
        ###### Set Style ###### 

    def setup_controller(self):
        pass

    
            
            
            
