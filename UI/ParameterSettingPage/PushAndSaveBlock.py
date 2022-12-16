from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal
import xml.etree.ElementTree as ET
from time import sleep
import os
import shutil

class CaptureWorker(QThread):
    set_btn_enable_signal = pyqtSignal(bool)
    def __init__(self, data, capture):
        super().__init__()
        self.data = data
        self.capture = capture

    def run(self):
        self.set_btn_enable_signal.emit(False)
        self.capture.capture(path=self.data["saved_path"], focus_time = 4, save_time = 0.5, capture_num = 1)
        self.set_btn_enable_signal.emit(True)

class PushWorker(QThread):
    set_btn_enable_signal = pyqtSignal(bool)
    capture_signal = pyqtSignal()
    def __init__(self, data, tuning):
        super().__init__()
        self.data = data
        self.tuning = tuning
        self.is_capture = False

    def run(self):
        self.set_btn_enable_signal.emit(False)
        self.tuning.buildAndPushToCamera(self.data["exe_path"], self.data["project_path"], self.data["bin_name"])
        sleep(7)
        # for i in range(12):
        #     print(i)
        #     sleep(1)
        if self.is_capture:
            self.capture_signal.emit()
        else:
            self.set_btn_enable_signal.emit(True)

class PushAndSaveBlock(QWidget):
    alert_info_signal = pyqtSignal(str, str)

    def __init__(self, ui):
        super().__init__()
        self.ui = ui 
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

        self.btn_set_to_xml = QPushButton("寫入XML")
        VLayout.addWidget(self.btn_set_to_xml)

        self.btn_push_phone = QPushButton("推到手機")
        VLayout.addWidget(self.btn_push_phone)

        self.btn_capture = QPushButton("拍照")
        VLayout.addWidget(self.btn_capture)

        self.btn_push_phone_capture = QPushButton("推到手機 + 拍照")
        VLayout.addWidget(self.btn_push_phone_capture)

        self.btn_recover_param = QPushButton("參數復原")
        VLayout.addWidget(self.btn_recover_param)

    def update_UI(self):
        self.trigger_selector = self.ui.parameter_setting_page.trigger_selector
        self.data = self.ui.data
        self.config = self.ui.config
        self.tuning = self.ui.tuning
        self.capture = self.ui.capture
        self.logger = self.ui.logger
        if 'saved_dir_name' in self.data:
            self.lineEdits_dir_name.setText(self.data['saved_dir_name'])
        if 'saved_img_name' in self.data:
            self.lineEdits_img_name.setText(self.data['saved_img_name'] )

        self.push_worker = PushWorker(self.data, self.tuning)
        self.capture_worker = CaptureWorker(self.data, self.capture)

        self.btn_capture.clicked.connect(self.do_capture)
        self.push_worker.capture_signal.connect(self.capture_worker.start)
        self.push_worker.set_btn_enable_signal.connect(self.btn_enable)
        self.capture_worker.set_btn_enable_signal.connect(self.btn_enable)

    def setup_controller(self):
        self.btn_set_to_xml.clicked.connect(self.set_to_xml)
        self.btn_push_phone.clicked.connect(lambda: self.push_phone(is_capture=False))
        self.btn_push_phone_capture.clicked.connect(lambda: self.push_phone(is_capture=True))
        self.btn_recover_param.clicked.connect(self.recover_param)

    def set_data(self):
        self.trigger_selector.set_data()
        
        self.data['saved_dir_name'] = self.lineEdits_dir_name.text()
        self.data['saved_img_name'] = self.lineEdits_img_name.text()

        dir_name = self.data["saved_dir_name"]
        img_name = self.data["saved_img_name"]

        if dir_name=="": dir_name="test"
        self.ui.tuning.mkdir(dir_name)

        self.data["saved_path"] = "{}/{}".format(dir_name, img_name)

    def set_to_xml(self):
        param_value = self.ui.parameter_setting_page.param_modify_block.get_param_value()

        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        
        # param
        # config
        self.tuning.rule = config["rule"]
        self.tuning.xml_node = config["xml_node"]
        self.tuning.expand = config["expand"]
        self.tuning.data_node = config["data_node"]

        self.tuning.xml_path = self.data['xml_path']+config["file_path"]
        self.tuning.trigger_idx = self.data["trigger_idx"]
        self.tuning.param_names = config['param_names']
        self.tuning.key = self.data["page_key"]

        self.logger.signal.emit('set {} trigger_idx={} param to xml {}, '.format(self.data["page_key"], self.tuning.trigger_idx, config["file_path"]))
        self.tuning.setParamToXML(param_value)

    def push_phone(self, is_capture):
        if is_capture:
            self.set_data()
            path = self.data["saved_path"]
            if os.path.exists(path+".jpg"):
                self.alert_info_signal.emit("檔名重複", "檔名\n"+path+".jpg\n已存在，請重新命名")
                return
        self.set_to_xml()
        self.push_worker.is_capture = is_capture
        self.push_worker.start()

    

    def btn_enable(self, b):
        self.btn_set_to_xml.setEnabled(b)
        self.btn_capture.setEnabled(b)
        self.btn_push_phone.setEnabled(b)
        self.btn_push_phone_capture.setEnabled(b)
        self.btn_recover_param.setEnabled(b)

    def do_capture(self):
        print("PushAndSaveBlock do_capture")
        self.set_data()
        self.ui.project_setting_page.set_data()
        path = self.data["saved_path"]
        if os.path.exists(path+".jpg"):
            self.alert_info_signal.emit("檔名重複", "檔名\n"+path+".jpg\n已存在，請重新命名")
            return
        self.capture_worker.start()
        # self.ui.capture.capture(path=path, focus_time = 3, save_time = 0.5, capture_num = 1)

    def recover_param(self):
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        config_data = self.config[self.data["page_root"]][self.data["page_key"]]

        src = self.data["project_path"]+"_origin"+"/Scenario.Default/XML/"+config_data["file_path"]
        des = self.data["project_path"]+"/Scenario.Default/XML/"+config_data["file_path"]

        if not os.path.exists(src):
            self.logger.signal.emit("{} not found".format(src))
            return

        self.logger.signal.emit("overwrite {} from {}".format(config_data["file_path"], src))
        shutil.copyfile(src, des)

        self.ui.parameter_setting_page.trigger_selector.set_trigger_idx(self.data["trigger_idx"])

