from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)

class PushAndSaveBlock(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        VLayout = QVBoxLayout(self)

        title_wraper = QHBoxLayout()
        label_title = QLabel("Push and Save")
        label_title.setStyleSheet("background-color:rgb(72, 72, 72);")
        title_wraper.addWidget(label_title)
        VLayout.addLayout(title_wraper)

        gridLayout = QGridLayout()

        label = QLabel("資料夾名稱")
        label.setToolTip("要存入的資料夾名稱")
        gridLayout.addWidget(label, 0, 0)

        self.lineEdits_dir_name = QLineEdit()
        gridLayout.addWidget(self.lineEdits_dir_name, 0, 1)

        label = QLabel("圖片檔名")
        label.setToolTip("要存入的圖片檔名")
        gridLayout.addWidget(label, 1, 0)

        self.lineEdits_img_name = QLineEdit()
        gridLayout.addWidget(self.lineEdits_img_name, 1, 1)

        VLayout.addLayout(gridLayout)

        self.btn_push_phone = QPushButton("推到手機")
        VLayout.addWidget(self.btn_push_phone)

        self.btn_capture = QPushButton("拍照")
        VLayout.addWidget(self.btn_capture)

        self.btn_recover_data = QPushButton("參數復原")
        VLayout.addWidget(self.btn_recover_data)

    def setup_controller(self):
        pass

    def set_data(self):
        pass

