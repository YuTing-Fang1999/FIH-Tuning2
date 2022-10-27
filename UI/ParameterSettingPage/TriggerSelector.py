from PyQt5.QtWidgets import QComboBox

class TriggerSelector(QComboBox):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()

    def setup_UI(self):
        self.setStyleSheet("font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255);")

    def update_UI(self, aec_trigger_datas):
        self.data = self.ui.data
        item_names = ["lux_idx from {} to {},  gain from {} to {}".format(d[0], d[1], d[2], d[3])for d in aec_trigger_datas]
        self.clear()
        self.addItems(item_names)

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
