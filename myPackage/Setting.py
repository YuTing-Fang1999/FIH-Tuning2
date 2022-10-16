import pickle
import json
import os
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox
from PyQt5.Qt import Qt

import xml.etree.ElementTree as ET


class Setting():
    def __init__(self, ui):
        self.ui = ui
        self.read_setting()

    def read_setting(self):
        if os.path.exists('setting.pkl'):
            with open('setting.pkl', 'rb') as f:
                print("read setting")
                self.data = pickle.load(f)
                # import pprint
                # pp = pprint.PrettyPrinter(indent=4)
                # pp.pprint(self.data)
                # self.data.pop("mod_wnr24_aec_data_list")
                # self.data.pop("xml_path")
        else:
            print("找不到設定檔，重新生成一個新的設定檔")
            self.data = {}

    def write_setting(self):
        print('write_setting')
        # self.set_param()
        with open("setting.pkl", "wb") as outfile:
            pickle.dump(self.data, outfile)
