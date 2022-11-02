from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QSpacerItem, QSizePolicy
)

from .TriggerSelector import TriggerSelector
from .ParamModifyBlock import ParamModifyBlock
from .ParamRangeBlock import ParamRangeBlock
from .HyperSettingBlock import HyperSettingBlock
from .PushAndSaveBlock import PushAndSaveBlock
from .ISP_Tree import ISP_Tree

import os
import xml.etree.ElementTree as ET

class ParameterSettingPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        horizontalLayout = QHBoxLayout(self)

        self.ISP_tree = ISP_Tree(self.ui)
        horizontalLayout.addWidget(self.ISP_tree)

        ###### Left Part ######
        verticalLayout = QVBoxLayout()
        verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.trigger_selector = TriggerSelector(self.ui)
        verticalLayout.addWidget(self.trigger_selector)

        self.param_modify_block = ParamModifyBlock(self.ui)
        verticalLayout.addWidget(self.param_modify_block)

        self.push_and_save_block = PushAndSaveBlock(self.ui)
        verticalLayout.addWidget(self.push_and_save_block)

        verticalLayout.addItem(spacerItem)
        
        horizontalLayout.addLayout(verticalLayout)
        ###### Left Part ######

        ###### Middle Part ######
        verticalLayout = QVBoxLayout()
        self.param_range_block = ParamRangeBlock(self.ui)
        verticalLayout.addWidget(self.param_range_block)
        verticalLayout.addItem(spacerItem)
        horizontalLayout.addLayout(verticalLayout)
        ###### Middle Part ######

        ###### Right Part ######
        verticalLayout = QVBoxLayout()
        self.hyper_setting_block = HyperSettingBlock(self.ui)
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

    def update_UI(self):
        root, key = self.ui.data["page_root"], self.ui.data["page_key"]
        self.ISP_tree.update_UI()
        self.param_modify_block.update_UI(root, key)
        self.param_range_block.update_UI(root, key)
        self.hyper_setting_block.update_UI()
        self.push_and_save_block.update_UI()

        self.data = self.ui.data
        self.config = self.ui.config
        if "project_path" in self.data and os.path.exists(self.data["project_path"]):
            self.set_project(self.data["project_path"])

    def setup_controller(self):
        pass
        # self.trigger_selector.currentIndexChanged[int].connect(self.set_trigger_idx)
        # self.ISP_tree.tree.itemClicked.connect(self.change_param_page)

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
        self.trigger_selector.set_trigger_idx(0)

    
    
       


