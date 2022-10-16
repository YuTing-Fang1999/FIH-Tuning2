from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QSpacerItem, QSizePolicy
)

from .ParamModifyBlock import ParamModifyBlock
from .ParamRangeBlock import ParamRangeBlock
from .HyperSettingBlock import HyperSettingBlock

class Tab2(QWidget):
    def __init__(self):
        super(Tab2, self).__init__()
        self.ParamModifyBlock = []
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        horizontalLayout = QHBoxLayout(self)

        ###### Left Part ######
        verticalLayout = QVBoxLayout()

        verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.trigger_selector = QComboBox()
        self.trigger_selector.setStyleSheet("background-color: rgb(255, 255, 255);")
        verticalLayout.addWidget(self.trigger_selector)

        self.param_modify_block = ParamModifyBlock()
        verticalLayout.addWidget(self.param_modify_block)

        self.btn_push_phone = QPushButton("推到手機")
        verticalLayout.addWidget(self.btn_push_phone)

        self.btn_capture = QPushButton("拍照")
        verticalLayout.addWidget(self.btn_capture)

        self.btn_recover_params = QPushButton("參數復原")
        verticalLayout.addWidget(self.btn_recover_params)

        verticalLayout.addItem(spacerItem)
        
        horizontalLayout.addLayout(verticalLayout)
        ###### Left Part ######

        ###### Middle Part ######
        verticalLayout = QVBoxLayout()
        self.param_range_block = ParamRangeBlock()
        verticalLayout.addWidget(self.param_range_block)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Middle Part ######

        ###### Right Part ######
        verticalLayout = QVBoxLayout()
        self.hyper_setting_block = HyperSettingBlock()
        verticalLayout.addWidget(self.hyper_setting_block)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Right Part ######

        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                          "QLineEdit{background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}"
                          "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}")

