from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTabWidget
)
from PyQt5 import QtCore

class UpperPart(QWidget):
    def __init__(self):
        super().__init__()

        horizontalLayout = QHBoxLayout(self)

        self.btn_run = QPushButton("Run")
        self.btn_run.setStyleSheet("font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        horizontalLayout.addWidget(self.btn_run)

        self.btn_param_window = QPushButton("Param")
        self.btn_param_window.setStyleSheet("font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        horizontalLayout.addWidget(self.btn_param_window)

        label = QLabel("總分")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        horizontalLayout.addWidget(label)

        self.label_score = QLabel("#")
        horizontalLayout.addWidget(self.label_score)

        gridLayout_gen = QGridLayout()

        label = QLabel("generation:")
        gridLayout_gen.addWidget(label, 0, 0, 1, 1)

        label = QLabel("individual:")
        gridLayout_gen.addWidget(label, 1, 0, 1, 1)

        self.label_generation = QLabel("#")
        gridLayout_gen.addWidget(self.label_generation, 0, 1, 1, 1)

        self.label_individual = QLabel("#")
        gridLayout_gen.addWidget(self.label_individual, 1, 1, 1, 1)

        horizontalLayout.addLayout(gridLayout_gen)

        self.label_time = QLabel("Time")
        self.label_time.setAlignment(QtCore.Qt.AlignCenter)
        self.label_time.setStyleSheet(
            "font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        horizontalLayout.addWidget(self.label_time)

class TabPlot(QWidget):
    def __init__(self, name):
        super().__init__()

        plot_wraprt = QVBoxLayout(self)
        self.label_plot = QLabel(name)
        self.label_plot.setAlignment(QtCore.Qt.AlignCenter)
        self.label_plot.setStyleSheet("background-color:rgb(0, 0, 0)")
        plot_wraprt.addWidget(self.label_plot)

class LowerPart(QTabWidget):
    def __init__(self):
        super().__init__()

        self.tab_score = TabPlot("分數圖")
        self.addTab(self.tab_score, "分數圖")

        self.tab_hyper = TabPlot("超參數")
        self.addTab(self.tab_hyper, "超參數")

        self.tab_loss = TabPlot("loss")
        self.addTab(self.tab_loss, "loss")

        self.tab_update = TabPlot("update rate")
        self.addTab(self.tab_update, "update rate")

class Tab3(QWidget):
    def __init__(self):
        super(Tab3, self).__init__()

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
