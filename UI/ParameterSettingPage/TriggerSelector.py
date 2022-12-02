from PyQt5.QtWidgets import QComboBox
import xml.etree.ElementTree as ET
import json

class TriggerSelector(QComboBox):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        self.setStyleSheet("font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255);")

    def update_UI(self, aec_trigger_datas):
        self.logger = self.ui.logger
        self.parameter_setting_page = self.ui.parameter_setting_page
        self.data = self.ui.data
        self.config = self.ui.config
        item_names = ["lux_idx from {} to {},  gain from {} to {}".format(d[0], d[1], d[2], d[3])for d in aec_trigger_datas]
        self.clear()
        self.addItems(item_names) # -> set_trigger_idx

    def setup_controller(self):
        self.currentIndexChanged[int].connect(self.set_trigger_idx)

    def set_trigger_idx(self, trigger_idx, xml_path=''):
        if trigger_idx==-1:
            self.logger.signal.emit("set_trigger_idx return because trigger_idx=-1")
            return
        self.logger.signal.emit('trigger_idx: {}'.format(trigger_idx))

        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]

        self.data["trigger_idx"] = trigger_idx
        self.data["trigger_name"] = self.currentText()

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
                rgn_data = ele.find(config["data_node"])
                for param_name in config['param_names']:
                    parent = rgn_data.find(param_name+'_tab')
                    if parent:
                        print(parent.find(param_name).text)
                        param_value = parent.find(param_name).text.split(' ') 
                        param_value = [float(x) for x in param_value]

                        bound = json.loads(parent.attrib['range'])
                        length = int(parent.attrib['length'])
                        
                    else:
                        parent = rgn_data.find(param_name)
                        param_value = parent.text.split(' ') 
                        param_value = [float(x) for x in param_value]

                        bound = json.loads(parent.attrib['range'])
                        length = int(parent.attrib['length'])

                    # ASF 暫定64取1
                    if param_name in ["layer_1_gain_positive_lut",
                                        "layer_1_gain_negative_lut",
                                        "layer_1_gain_weight_lut"]:
                        param_value = [param_value[0]]
                        length = 1
                    
                    # ABF 暫定2取1
                    if param_name in ["noise_prsv_lo",
                                        "noise_prsv_hi"]:
                        param_value = [param_value[0]]
                        length = 1

                    # WNR 暫定2取1
                    if param_name in ["denoise_weight_y", "denoise_weight_chroma"]:
                        param_value = [param_value[0],param_value[2]]
                        length = 2

                    block_data['dimensions'] += length
                    block_data['lengths'].append(length)
                    block_data['defult_range'].append(bound)
                    block_data['param_value'].append(param_value)
                break

        # converting 2d list into 1d
        block_data['param_value'] = sum(block_data['param_value'], [])
        # print(block_data['param_value'])

        self.parameter_setting_page.param_modify_block.update_param_value_UI(block_data['param_value'])
        self.parameter_setting_page.param_range_block.update_defult_range_UI(block_data['defult_range'])

