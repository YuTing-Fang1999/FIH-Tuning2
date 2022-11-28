from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QScrollArea,
    QPushButton, QLabel, QLineEdit, QFileDialog, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from .PlatformSelecter import PlatformSelecter
import os

class ProjectSettingPage(QWidget):
    set_project_signal = pyqtSignal(str)
    alert_info_signal = pyqtSignal(str, str)

    def __init__(self, ui):
        super().__init__()
        self.defult_path = "./" 
        self.row=0
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        Spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.createForm()

        HLayout = QHBoxLayout()
        HLayout.addSpacerItem(Spacer)
        HLayout.addLayout(self.gridLayout)
        HLayout.addSpacerItem(Spacer)
        HLayout.setAlignment(Qt.AlignCenter)

        #Scroll Area Properties
        scroll_wrapper = QHBoxLayout(self)
        layout_wrapper = QWidget()
        layout_wrapper.setLayout(HLayout)
        scroll = QScrollArea() 
        scroll.setWidgetResizable(True)
        scroll.setWidget(layout_wrapper)
        scroll_wrapper.addWidget(scroll)

        # Set Style
        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                           "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
                           "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}")


    def createForm(self):
        self.gridLayout = QGridLayout()

        self.btn_select_project = QPushButton("選擇project")
        self.btn_select_project.setToolTip("選擇tuning project folder")
        self.label_project_path = QLabel("")
        
        self.btn_select_exe = QPushButton("選擇ParameterParser")
        self.btn_select_exe.setToolTip("選擇ParameterParser.exe")
        self.label_exe_path = QLabel("")

        label_bin_name = QLabel("bin檔名稱")
        label_bin_name.setToolTip("將project編譯過後的bin檔名")
        self.lineEdits_bin_name = QLineEdit("")

        label_platfoem = QLabel("平台選擇")
        label_platfoem.adjustSize()
        self.platform_selecter = PlatformSelecter(self.ui)

        self.addRow(label_platfoem, self.platform_selecter)
        self.addRow(self.btn_select_project, self.label_project_path)
        self.addRow(self.btn_select_exe, self.label_exe_path)
        self.addRow(label_bin_name, self.lineEdits_bin_name)

    def addRow(self, w1, w2):
        self.gridLayout.addWidget(w1, self.row, 0, 1, 1)
        self.gridLayout.addWidget(w2, self.row, 1, 1, 1)
        self.row+=1

    def update_UI(self):
        self.data = self.ui.data
        self.platform_selecter.update_UI()
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
        # self.data.pop("OPE")

        self.ui.parameter_setting_page.set_project(folder_path)

    def select_exe(self):
        filename, filetype = QFileDialog.getOpenFileName(self,"選擇ParameterParser",self.defult_path) # start path
        if filename == "": return
        self.filename = filename
        self.label_exe_path.setText(filename)
        self.data["exe_path"] = filename

    def set_data(self, alert=True):
        print('set ProjectSettingPage data')
        self.data["project_path"] = self.label_project_path.text()
        self.data["exe_path"] = self.label_exe_path.text()
        self.data["bin_name"] = self.lineEdits_bin_name.text()
        if not os.path.exists(self.data["project_path"]) and alert:
            self.alert_info_signal.emit("找不到project_path", "找不到project_path: "+self.data["project_path"])
            return False

        if not os.path.exists(self.data["exe_path"]) and alert:
            self.alert_info_signal.emit("找不到exe_path", "找不到exe_path: "+self.data["exe_path"])
            return False

        if self.data["bin_name"]=="" and alert:
            self.alert_info_signal.emit("bin檔名稱未填寫", "請填寫bin檔名稱\n注意bin檔名稱一定要填正確")
            return False

