from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

class ProjectSettingPage(QWidget):
    set_project_signal = pyqtSignal(str)

    def __init__(self, ui):
        super().__init__()
        self.defult_path = "./" 
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        gridLayout = QGridLayout(self)

        self.btn_select_project = QPushButton("選擇project")
        self.btn_select_project.setToolTip("選擇tuning project folder")
        gridLayout.addWidget(self.btn_select_project, 0, 0)

        self.label_project_path = QLabel("")
        gridLayout.addWidget(self.label_project_path, 0, 1)

        self.btn_select_exe = QPushButton("選擇ParameterParser")
        self.btn_select_exe.setToolTip("選擇ParameterParser.exe")
        gridLayout.addWidget(self.btn_select_exe, 1, 0)

        self.label_exe_path = QLabel("")
        gridLayout.addWidget(self.label_exe_path, 1, 1)

        label = QLabel("bin檔名稱")
        label.setToolTip("將project編譯過後的bin檔名")
        gridLayout.addWidget(label, 2, 0)

        self.lineEdits_bin_name = QLineEdit("")
        gridLayout.addWidget(self.lineEdits_bin_name, 2, 1)

        # Set Style
        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                           "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
                           "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}")


    def update_UI(self):
        self.data = self.ui.data
        if "project_path" in self.data:
            self.label_project_path.setText(self.data["project_path"])
        if "exe_path" in self.data:
            self.label_exe_path.setText(self.data["exe_path"])
        if "bin_name" in self.data:
            self.lineEdits_bin_name.setText(self.data["bin_name"])

    def setup_controller(self):
        self.btn_select_project.clicked.connect(self.select_project)
        self.btn_select_exe.clicked.connect(self.select_exe)

    def select_project(self):
        folder_path = QFileDialog.getExistingDirectory(self,"選擇project",self.defult_path) # start path
        if folder_path == "": return
        self.defult_path = folder_path
        self.label_project_path.setText(folder_path)
        self.data["project_path"] = folder_path

        self.ui.parameter_setting_page.set_project()

    def select_exe(self):
        filename, filetype = QFileDialog.getOpenFileName(self,"選擇ParameterParser",self.defult_path) # start path
        if filename == "": return
        self.filename = filename
        self.label_exe_path.setText(filename)
        self.data["exe_path"] = filename

    def set_data(self):
        print('set ProjectSettingPage data')
        self.data["project_path"] = self.label_project_path.text()
        self.data["exe_path"] = self.label_exe_path.text()
        self.data["bin_name"] = self.lineEdits_bin_name.text()
