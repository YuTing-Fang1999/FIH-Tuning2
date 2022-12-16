from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

import pickle
import os
import xml.etree.ElementTree as ET
import json

class Setting(QWidget):
    alert_info_signal = pyqtSignal(str, str)
    
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.read_setting()

    def set_data(self, alert=True):
        print('setting: set data')
        if not self.ui.project_setting_page.set_data(alert) and alert:
            self.alert_info_signal.emit("資料有誤或未填完", "「選擇project」的資料未填完")
            return False

        if self.ui.ROI_setting_page.set_data() and alert:
            self.alert_info_signal.emit("資料有誤或未填完", "「ROI設定」的資料未填完")
            return False

        if not self.ui.parameter_setting_page.param_modify_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "「參數設定」未填完\n有參數打勾卻未填入數字")
            return False

        if not self.ui.parameter_setting_page.param_range_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "「參數設定」未填完\n參數範圍未填完")
            return False
        
        if not self.ui.parameter_setting_page.hyper_setting_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "「參數設定」未填完\n超參數未填完")
            return False

        self.ui.parameter_setting_page.trigger_selector.set_data()

        self.ui.run_page.upper_part.set_data()

        return True

    def read_setting(self):
        if os.path.exists('setting.json'):
            with open('setting.json', 'r') as f:
                self.data = json.load(f)

        else:
            print("找不到設定檔，重新生成一個新的設定檔")
            self.data = {
                "page_root": "OPE",
                "page_key": "WNR"
            }

    def write_setting(self):
        print('write_setting')
        with open("setting.json", "w") as outfile:
            outfile.write(json.dumps(self.data, indent=4))

