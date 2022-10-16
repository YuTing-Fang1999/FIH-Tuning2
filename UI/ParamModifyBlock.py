from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)

from PyQt5 import QtCore
class ParamModifyItem(QVBoxLayout):

    def __init__(self, title, name, col):
        super().__init__()
        self.title = title
        self.name = name
        self.checkBoxes_title = []
        self.checkBoxes = []
        self.lineEdits = []

        gridLayout = QGridLayout()
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setHorizontalSpacing(7)

        title_wraper = QHBoxLayout()
        label_title = QLabel(title)
        # label_title.setText(title)
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

        gridLayout.setColumnStretch(0, 1)

        self.addLayout(title_wraper)
        self.addLayout(gridLayout)

        self.checkBoxes_title.clicked.connect(self.toggle_title_checkBoxes)

    def toggle_title_checkBoxes(self):
        checked = self.checkBoxes_title.isChecked()
        for box in self.checkBoxes:
            box.setChecked(checked)

class ParamModifyBlock(QWidget):
    def __init__(self):
        super().__init__()
        title = ["Noise Profile", "Denoise Scale", "Denoise Edge Softness", "Denoise Weight"]
        name = [["Y", "Cb", "Cr"],["Y", "Chroma"],["Y", "Chroma"],["Y", "Chroma"]]
        col = [[3, 4, 4],[3, 4],[3, 4],[3, 4]]

        verticalLayout = QVBoxLayout(self)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        for i in range(len(title)):
            verticalLayout.addLayout(ParamModifyItem(title[i], name[i], col[i]))

    def set_project(self, project_path):

