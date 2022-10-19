from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt

class HyperSettingBlock(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data

        self.lineEdits_hyper_setting = []
        
        gridLayout = QGridLayout(self)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setHorizontalSpacing(7)

        text = ["population size", "generations", "capture num"] # "F", "Cr", 
        tip = ["要初始化幾組參數(不可小於5)\n實際使用建議為10", "總共跑幾輪", "每次計算分數時要拍幾張照片"] # "變異的程度(建議不要超過1)", "替換掉參數的比率(建議不要超過0.5)", 
        self.hyper_param_title = text
        for i in range(len(text)):
            label = QLabel(text[i])

            lineEdit = QLineEdit()
            label.setToolTip(tip[i])
            self.lineEdits_hyper_setting.append(lineEdit)

            gridLayout.addWidget(label, i, 0)
            gridLayout.addWidget(lineEdit, i, 1)