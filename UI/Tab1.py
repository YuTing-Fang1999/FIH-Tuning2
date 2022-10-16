from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit
)
from .ROI_Setting_Widget import ROI_Setting_Widget

class Tab1(QWidget):
    def __init__(self):
        super(Tab1, self).__init__()

        ###### Upper Part ###### 
        gridLayout = QGridLayout()

        self.btn_select_project = QPushButton("選擇project")
        self.btn_select_project.setToolTip("選擇tuning project folder")
        gridLayout.addWidget(self.btn_select_project, 0, 0)

        self.label_project_path = QLabel("")
        gridLayout.addWidget(self.label_project_path, 0, 1)

        self.btn_select_exe = QPushButton("選擇ParameterParser")
        self.btn_select_exe.setToolTip("選擇ParameterParser.exe")
        gridLayout.addWidget(self.btn_select_exe, 1, 0)

        self.label_exe_path = QLabel("")
        gridLayout.addWidget(self.label_exe_path, 1, 1)

        label = QLabel("bin檔名稱")
        label.setToolTip("將project編譯過後的bin檔名")
        gridLayout.addWidget(label, 2, 0)

        self.lineEdits_bin_name = QLineEdit("")
        gridLayout.addWidget(self.lineEdits_bin_name, 2, 1)
        ###### Upper Part ###### 


        ###### Lower Part ###### 
        self.ROI_setting_widget = ROI_Setting_Widget()
        ###### Lower Part ###### 


        parentGridLayout = QGridLayout(self)
        parentGridLayout.addLayout(gridLayout, 0, 0, 1, 1) # Upper Part
        parentGridLayout.addWidget(self.ROI_setting_widget, 1, 0, 1, 1) # Lower Part

        ###### Set Stretch ###### 
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 8)
        ###### Set Stretch ###### 

        ###### Set Style ###### 
        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                          "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
                          "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}")
        ###### Set Style ###### 
