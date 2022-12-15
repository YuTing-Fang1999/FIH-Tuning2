from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QSizePolicy
)

from PyQt5 import QtCore
from .CurveSlider import CurveSlider

class GridModifyItem(QWidget):

    def __init__(self, title, name, col):
        super().__init__()

        self.title = title
        self.name = name
        self.col = col
        self.checkBoxes_title = []
        self.checkBoxes = []
        self.lineEdits = []

        VLayout = QVBoxLayout(self)

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setHorizontalSpacing(7)

        title_wraper = QHBoxLayout()
        label_title = QLabel(title)
        label_title.setStyleSheet("background-color:rgb(72, 72, 72);")
        title_wraper.addWidget(label_title)

        self.checkBoxes_title = QCheckBox()
        title_wraper.addWidget(self.checkBoxes_title)
        VLayout.addLayout(title_wraper)

        idx = len(self.checkBoxes)
        # for i in range(sum(col)):
        #     checkBox = QCheckBox()
        #     checkBox.setToolTip("打勾代表將值固定")
        #     self.checkBoxes.append(checkBox)

        #     lineEdit = QLineEdit()
        #     self.lineEdits.append(lineEdit)

        for i in range(len(col)):

            label_name = QLabel()
            label_name.setText(name[i])
            label_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            
            label_name.setAlignment(QtCore.Qt.AlignRight)
            gridLayout.addWidget(label_name, i, 0)

            self.checkBoxes.append([])
            self.lineEdits.append([])

            for j in range(col[i]):
                checkBox = QCheckBox()
                checkBox.setToolTip("打勾代表將值固定")

                lineEdit = QLineEdit()

                gridLayout.addWidget(checkBox, i, 2+j*2)

                if name[i] == "layer_1_gain_weight_lut":
                    self.slider = CurveSlider()
                    gridLayout.addWidget(self.slider, i, 1+j*2)
                else:
                    gridLayout.addWidget(lineEdit, i, 1+j*2)

                self.checkBoxes[-1].append(checkBox)
                self.lineEdits[-1].append(lineEdit)
            

        VLayout.addLayout(gridLayout)

        self.checkBoxes_title.clicked.connect(self.toggle_title_checkBoxes)

    def toggle_title_checkBoxes(self):
        checked = self.checkBoxes_title.isChecked()
        for row_box in self.checkBoxes:
            for col_box in row_box:
                col_box.setChecked(checked)

class ParamModifyBlock(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()    

    def setup_UI(self):
        self.VLayout = QVBoxLayout(self)
        self.VLayout.setContentsMargins(0, 0, 0, 0)

    def reset_UI(self):
        # delete
        for i in range(self.VLayout.count()):
            self.VLayout.itemAt(i).widget().deleteLater()

    def update_UI(self, root, key):
        self.data = self.ui.data
        self.config = self.ui.config

        config = self.config[root][key]
        if root not in self.data: self.data[root]={}
        if key not in self.data[root]: self.data[root][key]={}
        self.root = root
        self.key = key

        self.reset_UI()

        self.param_modify_items = []
        for i in range(len(config["title"])):
                item = GridModifyItem(config["title"][i], config["name"][i], config["col"][i])
                self.param_modify_items.append(item)
                self.VLayout.addWidget(item)

        block_data = self.data[root][key]
        if "param_change_idx" in block_data:
            idx = 0
            for item in self.param_modify_items:
                for i in range(len(item.col)):
                    for j in range(item.col[i]):
                        if idx in block_data['param_change_idx']:
                            item.checkBoxes[i][j].setChecked(True)
                        idx += 1


    def update_param_value_UI(self, param_value):
        print('update ParamModifyBlock UI')
        idx = 0
        for item in self.param_modify_items:
            for i in range(len(item.col)):
                if item.name[i] == "layer_1_gain_weight_lut":
                    item.slider.s1.setValue(int(param_value[idx]*2))
                    idx +=1
                else:
                    for j in range(item.col[i]):
                        item.lineEdits[i][j].setText(str(param_value[idx]))
                        item.lineEdits[i][j].setCursorPosition(0)
                        idx += 1

    def set_data(self):
        print('set ParamModifyBlock data')

        param_change_idx = []
        param_value = []
        idx = 0
        for item in self.param_modify_items:
            for i in range(len(item.col)):
                if item.name[i] == "layer_1_gain_weight_lut":
                    param_value.append(item.slider.s1.value()/2)
                    idx += 1
                else:
                    for j in range(item.col[i]):
                        if item.checkBoxes[i][j].isChecked(): #代表要調
                            param_change_idx.append(idx)
                            
                        else: # 代表固定
                            if item.lineEdits[i][j].text() == "": 
                                print(item.title, "有參數沒打勾(代表固定)卻未填入數字")
                                return False
                                
                        param_value.append(float(item.lineEdits[i][j].text()))
                        idx += 1

        self.data[self.root][self.key]['param_change_idx'] = param_change_idx
        self.data[self.root][self.key]['param_value'] = param_value
        print(param_value)

        return True


    def get_param_value(self):
        print('get ParamModifyBlock param_value')

        param_value = []
        idx = 0
        for item in self.param_modify_items:
            for i in range(len(item.col)):
                if item.name[i] == "layer_1_gain_weight_lut":
                        param_value.append(item.slider.s1.value()/2)
                else:
                    for j in range(item.col[i]):
                        if item.lineEdits[i][j].text() == "":
                            print(item.title, "未填入數字")
                            return
                        else:
                            param_value.append(float(item.lineEdits[i][j].text()))
                idx += 1

        return param_value


    

