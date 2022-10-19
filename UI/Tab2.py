from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QSpacerItem, QSizePolicy
)

from .ParamModifyBlock import ParamModifyBlock
from .ParamRangeBlock import ParamRangeBlock
from .HyperSettingBlock import HyperSettingBlock
from .ISP_Tree import ISP_Tree

import os
import xml.etree.ElementTree as ET
import json

class TriggerSelector(QComboBox):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setStyleSheet("font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255);")

    def updataUI(self, aec_trigger_datas):
        item_names = ["lux_idx from {} to {},  gain from {} to {}".format(d[0], d[1], d[2], d[3])for d in aec_trigger_datas]
        self.clear()
        self.addItems(item_names)


class Tab2(QWidget):
    def __init__(self, data, config):
        super(Tab2, self).__init__()
        self.data = data
        self.config = config
        self.setupUi()
        self.setupController()

        if "project_path" in data and os.path.exists(data["project_path"]):
            self.set_project(data["project_path"])


    def setupUi(self):
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        horizontalLayout = QHBoxLayout(self)

        self.ISP_tree = ISP_Tree(self.config)
        horizontalLayout.addWidget(self.ISP_tree)

        ###### Left Part ######
        verticalLayout = QVBoxLayout()
        verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.trigger_selector = TriggerSelector(self.data)
        verticalLayout.addWidget(self.trigger_selector)

        self.param_modify_block = ParamModifyBlock(self.data, self.config)
        verticalLayout.addWidget(self.param_modify_block)

        self.btn_push_phone = QPushButton("推到手機")
        verticalLayout.addWidget(self.btn_push_phone)

        self.btn_capture = QPushButton("拍照")
        verticalLayout.addWidget(self.btn_capture)

        self.btn_recover_data = QPushButton("參數復原")
        verticalLayout.addWidget(self.btn_recover_data)

        verticalLayout.addItem(spacerItem)
        
        horizontalLayout.addLayout(verticalLayout)
        ###### Left Part ######

        ###### Middle Part ######
        verticalLayout = QVBoxLayout()
        self.param_range_block = ParamRangeBlock(self.data, self.config)
        verticalLayout.addWidget(self.param_range_block)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Middle Part ######

        ###### Right Part ######
        verticalLayout = QVBoxLayout()
        self.hyper_setting_block = HyperSettingBlock(self.data)
        verticalLayout.addWidget(self.hyper_setting_block)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Right Part ######

        # Set Style
        self.setStyleSheet(
            "QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
            "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
            "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}"
        )


    def setupController(self):
        self.trigger_selector.currentIndexChanged[int].connect(self.set_trigger_idx)

    def set_project(self, folder_path):
        self.data['project_path'] = folder_path
        self.data['project_name'] = folder_path.split('/')[-1]
        self.data['tuning_dir'] = '/'.join(folder_path.split('/')[:-1])
        self.data['xml_path'] = folder_path + '/Scenario.Default/XML/OPE/wnr24_ope.xml'
        self.set_project_XML(self.data['xml_path'])

    def set_project_XML(self, xml_path):
        # 從檔案載入並解析 XML 資料
        if not os.path.exists(xml_path):
            print('No such file:', xml_path)
            return

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_wnr24_aec_datas  =  root.findall("chromatix_wnr24_core/mod_wnr24_post_scale_ratio_data/"\
                            "post_scale_ratio_data/mod_wnr24_pre_scale_ratio_data/"\
                            "pre_scale_ratio_data/mod_wnr24_total_scale_ratio_data/"\
                            "total_scale_ratio_data/mod_wnr24_drc_gain_data/"\
                            "drc_gain_data/mod_wnr24_hdr_aec_data/hdr_aec_data/"\
                            "mod_wnr24_aec_data"
                            )
        # hdr_aec_data 下面有多組 gain 的設定 (mod_wnr24_aec_data)
        # 每組mod_wnr24_aec_data分別有 aec_trigger 與 wnr24_rgn_data
        # 其中 aec_trigger 代表在甚麼樣的ISO光源下觸發
        # wnr24_rgn_data 代表所觸發的參數

        aec_trigger_datas = []
        for ele in mod_wnr24_aec_datas:
            data = []
            aec_trigger = ele.find("aec_trigger")
            data.append(aec_trigger.find("lux_idx_start").text)
            data.append(aec_trigger.find("lux_idx_end").text)
            data.append(aec_trigger.find("gain_start").text)
            data.append(aec_trigger.find("gain_end").text)
            aec_trigger_datas.append(data)

        self.trigger_selector.updataUI(aec_trigger_datas)

    def set_trigger_idx(self, trigger_idx, xml_path=''):
        print('trigger_idx', trigger_idx)
        self.data["trigger_idx"] = trigger_idx

        if xml_path=='' and 'xml_path' in self.data: xml_path=self.data['xml_path']
        if xml_path=='': return

        self.data['dimensions'] = 0
        self.data['lengths'] = []
        self.data['defult_range'] = []
        self.data['param_value'] = []

        # 從檔案載入並解析 XML 資料
        if xml_path=='': xml_path=self.data['xml_path']
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_wnr24_aec_datas  =  root.findall("chromatix_wnr24_core/mod_wnr24_post_scale_ratio_data/"\
                            "post_scale_ratio_data/mod_wnr24_pre_scale_ratio_data/"\
                            "pre_scale_ratio_data/mod_wnr24_total_scale_ratio_data/"\
                            "total_scale_ratio_data/mod_wnr24_drc_gain_data/"\
                            "drc_gain_data/mod_wnr24_hdr_aec_data/hdr_aec_data/"\
                            "mod_wnr24_aec_data"
                            )

        for i, ele in enumerate(mod_wnr24_aec_datas):
            if i==trigger_idx:
                wnr24_rgn_data = ele.find("wnr24_rgn_data")
                for param_name in self.data['param_names']:
                    parent = wnr24_rgn_data.find(param_name+'_tab')
                    # print(param_name, length, param_value, bound)

                    param_value = parent.find(param_name).text.split(' ')
                    param_value = [float(x) for x in param_value]

                    bound = json.loads(parent.attrib['range'])
                    length = int(parent.attrib['length'])

                    self.data['dimensions'] += length
                    self.data['lengths'].append(length)
                    self.data['defult_range'].append(bound)
                    self.data['param_value'].append(param_value)
                break

        # converting 2d list into 1d
        self.data['param_value'] = sum(self.data['param_value'], [])

        self.param_modify_block.update_param_value_UI(self.data['param_value'])
        self.param_range_block.update_defult_range_UI(self.data['defult_range'])


