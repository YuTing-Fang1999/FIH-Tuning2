from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal

class PlatformSelecter(QWidget):

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()

    def setup_UI(self):
        HLayout = QHBoxLayout(self)

        self.rb1 = QRadioButton('c7project',self)
        self.rb2 = QRadioButton('c6project',self)

        HLayout.addWidget(self.rb1)
        HLayout.addWidget(self.rb2)
        HLayout.setAlignment(Qt.AlignLeft)

        self.buttongroup1 = QButtonGroup(self)
        self.buttongroup1.addButton(self.rb1, 1)
        self.buttongroup1.addButton(self.rb2, 2)

        self.rb1.setChecked(True)
        self.type = self.rb1.text()

        self.buttongroup1.buttonClicked.connect(self.onButtonGroup1Click)

        # Set Style
        self.setStyleSheet("QRadioButton{font-size:12pt; font-family:微軟正黑體; color:white;}"
                           "QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}")

    def update_UI(self):
        self.data = self.ui.data

    def onButtonGroup1Click(self):
        if self.buttongroup1.checkedId() == 1:
            self.type = self.rb1.text()
            print(self.type)
            self.data["platform"]=self.rb1.text()

        if self.buttongroup1.checkedId() == 2:
            self.type = self.rb2.text()
            print(self.type)
            self.data["platform"]=self.rb1.text()
