from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QSpacerItem, QSizePolicy
)

from .ParamModifyBlock import ParamModifyBlock
from .ParamRangeBlock import ParamRangeBlock
from .HyperSettingBlock import HyperSettingBlock
from .PushAndSaveBlock import PushAndSaveBlock
from .ISP_Tree import ISP_Tree

import os
import xml.etree.ElementTree as ET
import json

class TriggerSelector(QComboBox):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setStyleSheet("font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255);")

    def update_UI(self, aec_trigger_datas):
        item_names = ["lux_idx from {} to {},  gain from {} to {}".format(d[0], d[1], d[2], d[3])for d in aec_trigger_datas]
        self.clear()
        self.addItems(item_names)


class Tab2(QWidget):
    def __init__(self, data, config):
        super(Tab2, self).__init__()
        self.data = data
        self.config = config
        self.setup_UI()
        self.update_UI()
        self.setup_controller()


    def setup_UI(self):
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

        self.push_and_save = PushAndSaveBlock()
        verticalLayout.addWidget(self.push_and_save)

        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Right Part ######

        # Set Style
        self.setStyleSheet(
            "QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
            "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
            "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}"
        )

    def update_UI(self):
        if "project_path" in self.data and os.path.exists(self.data["project_path"]):
            self.set_project(self.data["project_path"])

    def setup_controller(self):
        self.trigger_selector.currentIndexChanged[int].connect(self.set_trigger_idx)
        self.ISP_tree.tree.itemClicked.connect(self.change_param_page)

    def change_param_page(self, item, col):
        if item.parent() is None: 
            if item.isExpanded():item.setExpanded(False)
            else: item.setExpanded(True)
            return

        root = item.parent().text(0)
        key = item.text(0)
        print('change param page to', root, key)
        self.param_modify_block.update_UI(root, key)
        self.param_range_block.update_UI(root, key)
        self.data["page_root"] = root
        self.data["page_key"] = key
        self.set_trigger_idx(0)

    def set_project(self, folder_path):
        self.data['project_path'] = folder_path
        self.data['project_name'] = folder_path.split('/')[-1]
        self.data['tuning_dir'] = '/'.join(folder_path.split('/')[:-1])
        self.data['xml_path'] = folder_path + '/Scenario.Default/XML/'
        self.set_project_XML(self.data['xml_path'])

    def set_project_XML(self, xml_path):
        print('Read XML')
        if "page_root" not in self.data: 
            print('Return because no page root')
            return
        if "page_key" not in self.data: 
            print('Return because no page key')
            return
        
        config = self.config[self.data["page_root"]][self.data["page_key"]]
        xml_path+=config["file_path"]

        # 從檔案載入並解析 XML 資料
        if not os.path.exists(xml_path):
            print('Return because no such file:', xml_path)
            return

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_wnr24_aec_datas  =  root.findall(config["xml_node"])
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

        self.trigger_selector.update_UI(aec_trigger_datas)
        self.set_trigger_idx(0)

    def set_trigger_idx(self, trigger_idx, xml_path=''):
        print('trigger_idx', trigger_idx)

        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]

        block_data["trigger_idx"] = trigger_idx

        if xml_path=='' and 'xml_path' in self.data: xml_path=self.data['xml_path']+config["file_path"]
        if xml_path=='': return

        block_data['dimensions'] = 0
        block_data['lengths'] = []
        block_data['defult_range'] = []
        block_data['param_value'] = []

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 子節點與屬性
        node  =  root.findall(config["xml_node"])

        for i, ele in enumerate(node):
            if i==trigger_idx:
                wnr24_rgn_data = ele.find(config["data_node"])
                for param_name in config['param_names']:
                    parent = wnr24_rgn_data.find(param_name+'_tab')

                    param_value = parent.find(param_name).text.split(' ')
                    param_value = [float(x) for x in param_value]

                    bound = json.loads(parent.attrib['range'])
                    length = int(parent.attrib['length'])

                    block_data['dimensions'] += length
                    block_data['lengths'].append(length)
                    block_data['defult_range'].append(bound)
                    block_data['param_value'].append(param_value)
                break

        # converting 2d list into 1d
        block_data['param_value'] = sum(block_data['param_value'], [])

        self.param_modify_block.update_param_value_UI(block_data['param_value'])
        self.param_range_block.update_defult_range_UI(block_data['defult_range'])


