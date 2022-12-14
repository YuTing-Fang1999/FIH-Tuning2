from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt

class HyperSettingBlock(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.lineEdits_hyper_setting = []
        self.setup_UI()
        
    def setup_UI(self):
        VLayout = QVBoxLayout(self)

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setHorizontalSpacing(7)

        title_wraper = QHBoxLayout()
        label_title = QLabel("Hyper Parameters")
        label_title.setStyleSheet("background-color:rgb(72, 72, 72);")
        title_wraper.addWidget(label_title)

        self.hyper_param_name = ["population size", "generations", "capture num"] # "F", "Cr", 
        tip = ["要初始化幾組參數(不可小於5)\n實際使用建議為10", "總共跑幾輪", "每次計算分數時要拍幾張照片"] # "變異的程度(建議不要超過1)", "替換掉參數的比率(建議不要超過0.5)", 
        self.hyper_param_title = self.hyper_param_name
        for i in range(len(self.hyper_param_name)):
            label = QLabel(self.hyper_param_name[i])

            lineEdit = QLineEdit()
            label.setToolTip(tip[i])
            self.lineEdits_hyper_setting.append(lineEdit)

            gridLayout.addWidget(label, i, 0)
            gridLayout.addWidget(lineEdit, i, 1)

        VLayout.addLayout(title_wraper)
        VLayout.addLayout(gridLayout)

    def update_UI(self):
        self.data = self.ui.data
        for i in range(len(self.hyper_param_name)):
            if self.hyper_param_name[i] in self.data:
                self.lineEdits_hyper_setting[i].setText(str(self.data[self.hyper_param_name[i]]))

    def set_data(self):
        print("set hyper param data")
        fill=True
        for i in range(len(self.hyper_param_name)):
            if self.lineEdits_hyper_setting[i].text()=="":
                self.data[self.hyper_param_name[i]] = ""
                fill = False
            else:
                self.data[self.hyper_param_name[i]] = int(self.lineEdits_hyper_setting[i].text())
        return fill

