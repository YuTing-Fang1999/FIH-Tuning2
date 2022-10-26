from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt
import numpy as np
import json

class ParamRangeItem(QWidget):
    def __init__(self, title, name, row):
            super().__init__()
            self.label_defult_range = []
            self.lineEdits_range = []

            VLayout = QVBoxLayout(self)

            gridLayout = QGridLayout()
            gridLayout.setContentsMargins(0, 0, 0, 0)
            gridLayout.setHorizontalSpacing(7)

            label_title = QLabel(title)
            label_title.setStyleSheet("background-color:rgb(72, 72, 72);")

            gridLayout.addWidget(QLabel("預設範圍"), 0, 1)
            gridLayout.addWidget(QLabel("自訂範圍"), 0, 2)

            for i in range(row):
                label = QLabel()
                label.setText("#")
                self.label_defult_range.append(label)

                lineEdit = QLineEdit()
                self.lineEdits_range.append(lineEdit)

            for i in range(1, row+1):
                label_name = QLabel()
                label_name.setText(name[i-1])
                label_name.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
                gridLayout.addWidget(label_name, i, 0)

                gridLayout.addWidget(self.label_defult_range[i-1], i, 1)
                gridLayout.addWidget(self.lineEdits_range[i-1], i, 2)

            gridLayout.setColumnStretch(0, 2)
            gridLayout.setColumnStretch(1, 3)
            gridLayout.setColumnStretch(2, 3)

            VLayout.addWidget(label_title)
            VLayout.addLayout(gridLayout)


class ParamRangeBlock(QWidget):
    def __init__(self, data, config):
        super().__init__()
        self.data = data
        self.config = config
        self.root = self.data["page_root"]
        self.key = self.data["page_key"]

        # title = ["Noise Profile", "Denoise Scale", "Denoise Edge Softness", "Denoise Weight"]
        # name = [["Y", "Cb", "Cr"],["Y", "Chroma"],["Y", "Chroma"],["Y", "Chroma"]]
        # col = [[3, 4, 4],[3, 4],[3, 4],[3, 4]]
        self.VLayout = QVBoxLayout(self)
        self.VLayout.setContentsMargins(0, 0, 0, 0)
        self.update_UI(self.root, self.key)


    def update_UI(self, root, key):
        config = self.config[root][key]
        if root not in self.data: self.data[root]={}
        if key not in self.data[root]: self.data[root][key]={}
        self.root = root
        self.key = key

        # delete
        for i in range(self.VLayout.count()):
            self.VLayout.itemAt(i).widget().deleteLater()

        self.param_range_items = []
        for i in range(len(config["title"])):
            item = ParamRangeItem(config["title"][i], config["name"][i], len(config["col"][i]))
            self.param_range_items.append(item)
            self.VLayout.addWidget(item)
        

    def update_defult_range_UI(self, defult_range):
        print('update ParamRangeBlock UI')
        idx = 0
        for item in self.param_range_items:
            for label in item.label_defult_range:
                label.setText(str(defult_range[idx]))
                idx += 1
        
        self.data[self.root][self.key]["coustom_range"] = defult_range
        idx = 0
        for item in self.param_range_items:
            for lineEdit in item.lineEdits_range:
                lineEdit.setText(str(defult_range[idx]))
                idx += 1

    def set_data(self):
        print('set ParamRangeBlock data')
        config = self.config[self.root][self.key]
        block_data = self.data[self.root][self.key]
        block_data["coustom_range"] = []

        for item in self.param_range_items:
            for lineEdit in item.lineEdits_range:
                if lineEdit.text() == "": 
                    block_data["coustom_range"] = []
                    break
                block_data["coustom_range"].append(json.loads(lineEdit.text()))

        if len(block_data["coustom_range"]) > 0:
            block_data['bounds'] = [block_data['coustom_range'][0]]*block_data['lengths'][0]
            for i in range(1, len(block_data['lengths'])):
                block_data['bounds'] = np.concatenate([block_data['bounds'] , [block_data['coustom_range'][i]]*block_data['lengths'][i]])

            block_data['bounds']=block_data['bounds'].tolist()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    MainWindow.setCentralWidget(ParamRangeBlock())
    MainWindow.show()
    sys.exit(app.exec_())