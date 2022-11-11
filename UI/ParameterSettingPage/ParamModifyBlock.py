from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QSizePolicy
)

from PyQt5 import QtCore

class GridModifyItem(QWidget):

    def __init__(self, title, name, col):
        super().__init__()
        self.title = title
        self.name = name
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

        idx = len(self.checkBoxes)
        for i in range(sum(col)):
            checkBox = QCheckBox()
            checkBox.setToolTip("打勾代表將值固定")
            self.checkBoxes.append(checkBox)

            lineEdit = QLineEdit()
            self.lineEdits.append(lineEdit)

        for i in range(len(col)):
            label_name = QLabel()
            label_name.setText(name[i])
            
            label_name.setAlignment(QtCore.Qt.AlignRight)
            gridLayout.addWidget(label_name, i, 0)

            for j in range(col[i]):
                gridLayout.addWidget(self.checkBoxes[idx], i, 2+j*2)
                gridLayout.addWidget(self.lineEdits[idx], i, 1+j*2)
                idx += 1

        VLayout.addLayout(title_wraper)
        VLayout.addLayout(gridLayout)

        self.checkBoxes_title.clicked.connect(self.toggle_title_checkBoxes)

    def toggle_title_checkBoxes(self):
        checked = self.checkBoxes_title.isChecked()
        for box in self.checkBoxes:
            box.setChecked(checked)

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
            for P in self.param_modify_items:
                for i in range(len(P.checkBoxes)):
                    if idx not in block_data['param_change_idx']:
                        P.checkBoxes[i].setChecked(True)
                    idx += 1


    def update_param_value_UI(self, param_value):
        print('update ParamModifyBlock UI')
        idx = 0
        for item in self.param_modify_items:
            for lineEdit in item.lineEdits:
                lineEdit.setText(str(param_value[idx]))
                lineEdit.setCursorPosition(0)
                idx += 1

    def set_data(self):
        print('set ParamModifyBlock data')

        param_change_idx = []
        param_value = []
        idx = 0
        for P in self.param_modify_items:
            for i in range(len(P.checkBoxes)):
                if P.checkBoxes[i].isChecked():
                    if P.lineEdits[i].text() == "":
                        print(P.title, "有參數打勾卻未填入數字")
                        return False
                else:
                    param_change_idx.append(idx)
                if P.lineEdits[i].text() == '':
                    param_value.append(0)
                else:
                    param_value.append(float(P.lineEdits[i].text()))
                idx += 1

        self.data[self.root][self.key]['param_change_idx'] = param_change_idx
        self.data[self.root][self.key]['param_value'] = param_value


    

