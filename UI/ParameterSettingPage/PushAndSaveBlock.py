from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox
)
import xml.etree.ElementTree as ET
from time import sleep

class PushAndSaveBlock(QWidget):
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

        self.btn_push_phone = QPushButton("推到手機")
        VLayout.addWidget(self.btn_push_phone)

        self.btn_capture = QPushButton("拍照")
        VLayout.addWidget(self.btn_capture)

        self.btn_recover_param = QPushButton("參數復原")
        VLayout.addWidget(self.btn_recover_param)

    def update_UI(self):
        self.data = self.ui.data
        self.config = self.ui.config
        self.tuning = self.ui.tuning
        if 'saved_dir_name' in self.data:
            self.lineEdits_dir_name.setText(self.data['saved_dir_name'])
        if 'saved_img_name' in self.data:
            self.lineEdits_img_name.setText(self.data['saved_img_name'] )

    def setup_controller(self):
        self.btn_push_phone.clicked.connect(self.push_phone)
        self.btn_capture.clicked.connect(self.do_capture)
        self.btn_recover_param.clicked.connect(self.recover_param)

    def set_data(self):
        self.data['saved_dir_name'] = self.lineEdits_dir_name.text()
        self.data['saved_img_name'] = self.lineEdits_img_name.text()

    def push_phone(self):
        param_value = self.get_param_value()
        print(param_value)
        self.setParamToXML(param_value)
        self.tuning.buildAndPushToCamera()
        sleep(6)
        self.do_capture()

    def get_param_value(self):
        print('get ParamModifyBlock param_value')

        param_value = []
        idx = 0
        for P in self.ui.parameter_setting_page.param_modify_block.param_modify_items:
            for i in range(len(P.checkBoxes)):
                if P.lineEdits[i].text() == "":
                    print(P.title, "未填入數字")
                    return
                else:
                    param_value.append(float(P.lineEdits[i].text()))
                idx += 1
        return param_value


    def setParamToXML(self, param_value):
        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        
        # param
        self.xml_path = self.data['xml_path']+config["file_path"]
        self.xml_node = config["xml_node"]
        self.trigger_idx = block_data["trigger_idx"]
        self.param_names = config['param_names']

        print('set param to xml {}, trigger_idx={}'.format(self.xml_path, self.trigger_idx))

        # 從檔案載入並解析 XML 資料
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_aec_datas = root.findall(self.xml_node)

        for i, ele in enumerate(mod_aec_datas):
            if i==self.trigger_idx:
                wnr24_rgn_data = ele.find("wnr24_rgn_data")
                dim = 0
                for param_name in self.param_names:
                    parent = wnr24_rgn_data.find(param_name+'_tab')
                    length = int(parent.attrib['length'])

                    param_value_new = param_value[dim: dim+length]
                    param_value_new = [str(x) for x in param_value_new]
                    param_value_new = ' '.join(param_value_new)

                    # print('old param', wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)
                    wnr24_rgn_data.find(param_name+'_tab/' + param_name).text = param_value_new
                    # print('new param',wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)

                    dim += length
                break

        # write the xml file
        tree.write(self.xml_path, encoding='UTF-8', xml_declaration=True)


    def do_capture(self):
        self.set_data()
        dir_name = self.data["saved_dir_name"]
        img_name = self.data["saved_img_name"]
        if dir_name=="": 
            path=""
        else:
            self.ui.tuning.mkdir(dir_name)
            path = "{}/{}".format(dir_name, img_name)
        print("PushAndSaveBlock do_capture")
        self.ui.project_setting_page.set_data()
        self.ui.capture.capture(path=path, focus_time = 3, save_time = 0.5, capture_num = 1)

    def recover_param(self):
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        self.ui.parameter_setting_page.trigger_selector.set_trigger_idx(block_data["trigger_idx"], xml_path='C:/Users/s830s/OneDrive/文件/github/FIH/Tuning/oem/qcom/tuning/s5k3l6_c7project_origin/Scenario.Default/XML/OPE/wnr24_ope.xml')

