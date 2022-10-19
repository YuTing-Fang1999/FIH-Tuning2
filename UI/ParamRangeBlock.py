from PyQt5.QtWidgets import (
    QApplication, QMainWindow,
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt

class ParamRangeItem(QVBoxLayout):
    def __init__(self, title, name, row):
            super().__init__()
            self.label_defult_range = []
            self.lineEdits_range = []

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

            self.addWidget(label_title)
            self.addLayout(gridLayout)


class ParamRangeBlock(QWidget):
    def __init__(self, data, config):
        super().__init__()
        self.data = data
        self.config = config

        # title = ["Noise Profile", "Denoise Scale", "Denoise Edge Softness", "Denoise Weight"]
        # name = [["Y", "Cb", "Cr"],["Y", "Chroma"],["Y", "Chroma"],["Y", "Chroma"]]
        # col = [[3, 4, 4],[3, 4],[3, 4],[3, 4]]
        self.VLayout = QVBoxLayout(self)
        self.VLayout.setContentsMargins(0, 0, 0, 0)
        self.update_UI("WNR")


        

    def update_UI(self, key):
        config = self.config[key]

        self.param_range_items = []
        for i in range(len(config["title"])):
            item = ParamRangeItem(config["title"][i], config["name"][i], len(config["col"][i]))
            self.param_range_items.append(item)
            self.VLayout.addLayout(item)
        

    def update_defult_range_UI(self, defult_range):
        print('update_defult_range_UI')
        idx = 0
        for item in self.param_range_items:
            for label in item.label_defult_range:
                label.setText(str(defult_range[idx]))
                idx += 1

        # self.data["coustom_range"] = defult_range
        # idx = 0
        # for item in self.param_range_items:
        #     for lineEdit in item.lineEdits_range:
        #         lineEdit.setText(str(defult_range[idx]))
        #         idx += 1

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    MainWindow.setCentralWidget(ParamRangeBlock())
    MainWindow.show()
    sys.exit(app.exec_())