from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

import pickle
import os
import xml.etree.ElementTree as ET

class Setting(QWidget):
    alert_info_signal = pyqtSignal(str, str)
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.read_setting()

    def set_data(self, alert=True):
        if self.ui.tab1.project_setting.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "project部分的參數未填完")
            return False

        if self.ui.tab1.ROI_setting_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "ROI設置部分的參數未填完")
            return False

        if self.ui.tab2.param_modify_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "有參數打勾卻未填入數字")
            return False

        if self.ui.tab2.param_range_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "有參數打勾卻未填入數字")
            return False
        
        if self.ui.tab2.hyper_setting_block.set_data() and alert:
            self.alert_info_signal.emit("參數未填完", "超參數部分的參數未填完")
            return False

        return True

    def read_setting(self):
        if os.path.exists('setting.pkl'):
            with open('setting.pkl', 'rb') as f:
                print("read setting")
                self.data = pickle.load(f)
                
                # self.data.pop("mod_wnr24_aec_data_list")
                # self.data.pop("xml_path")
        else:
            print("找不到設定檔，重新生成一個新的設定檔")
            self.data = {
                "page_root": "OPE",
                "page_key": "WNR"
            }

        print("setting.pkl")
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.data)

    def write_setting(self):
        print('write_setting')
        self.set_data(alert=False)
        with open("setting.pkl", "wb") as outfile:
            pickle.dump(self.data, outfile)
