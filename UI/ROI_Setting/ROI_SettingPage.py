from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QSpacerItem, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,
    QPushButton, QLabel, QApplication, QCheckBox, QTableWidget, QHeaderView,
    QTableWidgetItem
)    
import cv2
import numpy as np
from copy import deepcopy

import sys
sys.path.append(".")

from ROI_Info import ROI_Info
from ImageViewer import ImageViewer
from ROI_Select_Window import ROI_Select_Window
from MeasureWindow import MeasureWindow
import os
import random

class DeleteBtn(QPushButton):
    def __init__(self, table):
        super().__init__()
        self.table = table
        self.setText("刪除")
        self.clicked.connect(self.deleteClicked)

    def deleteClicked(self):
        button = self.sender()
        if button:
            row = self.table.indexAt(button.pos()).row()
            self.table.removeRow(row)
            print("del row", row)

class ROI_SettingPage(QWidget):
    to_setting_signal = pyqtSignal(list, list, list)
    alert_info_signal = pyqtSignal(str, str)

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.idx=0
        self.region_id=0
        self.roi_info = []

        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        # Widgets
        self.label_img = ImageViewer()
        self.label_img.setAlignment(Qt.AlignCenter)
        self.label_img.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.ROI_select_window = ROI_Select_Window()
        self.measure_window = MeasureWindow()

        self.table = QTableWidget()
        self.headers = ["region id", "type", "score", "weight", "刪除紐"]
        self.table.setColumnCount(len(self.headers))   ##设置列数
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        QTableWidget.resizeRowsToContents(self.table)


        self.btn_capture = QPushButton()
        self.btn_capture.setText("拍攝照片")
        self.btn_capture.setToolTip("會拍攝一張照片，請耐心等候")

        self.btn_add_ROI_item = QPushButton()
        self.btn_add_ROI_item.setText("增加區域")
        self.btn_add_ROI_item.setToolTip("按下後會新增一個目標區域")

        self.GLayout = QGridLayout()
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Arrange layout
        HBlayout = QHBoxLayout(self)

        VBlayout = QVBoxLayout()
        VBlayout.addWidget(self.label_img)
        VBlayout.addWidget(self.btn_capture)
        VBlayout.addWidget(self.btn_add_ROI_item)
        HBlayout.addLayout(VBlayout)

        VBlayout = QVBoxLayout()
        # VBlayout.addLayout(self.GLayout)
        VBlayout.addWidget(self.table)
        # VBlayout.addItem(spacerItem)
        HBlayout.addLayout(VBlayout)

        HBlayout.setStretch(0,3)
        HBlayout.setStretch(1,2)


        self.setStyleSheet(
            "QWidget{background-color: rgb(66, 66, 66);}"
            "QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
            "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
            "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}")

    def setup_controller(self):
        self.ROI_select_window.to_main_window_signal.connect(self.select_ROI)
        self.measure_window.to_main_window_signal.connect(self.set_target_score)
        self.btn_add_ROI_item.clicked.connect(self.add_to_table)
        # self.btn_add_ROI_item.clicked.connect(self.add_ROI_item_click)
        self.btn_capture.clicked.connect(self.do_capture)
    
        
    def select_ROI(self, img_idx, my_x_y_w_h, target_roi_img):
        self.measure_window.measure_target(img_idx, my_x_y_w_h, target_roi_img)

    def set_target_score(self, region_id, my_x_y_w_h, target_type, score_value):
        for i in range(len(target_type)):
            self.add_ROI_item(target_type[i], score_value[i], 1)
            self.data["roi"].append(my_x_y_w_h)
            self.draw_ROI()

        self.region_id+=1

    def add_to_table(self):
        print("add_to_table")
        roi_info = ROI_Info(self.table, self.region_id, self.idx, "target_type", 0, 1)

        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        self.table.setCellWidget(row,0,QLabel(str(self.region_id)))
        self.table.setCellWidget(row,1,roi_info.type_selector)
        self.table.setCellWidget(row,2,roi_info.target_score)
        self.table.setCellWidget(row,3,roi_info.target_weight)
        self.table.setCellWidget(row,4,DeleteBtn(self.table))

        self.idx += 1
        
    def draw_ROI(self):
        if 'roi' in self.data:
            img_select = self.img.copy()
            print('draw_ROI', self.data["roi"])
            for i, roi in enumerate(self.data["roi"]):
                if len(roi)==0: continue

                x, y, w, h = roi
                # 隨機產生顏色
                color = [random.randint(0, 255), random.randint(0, 255),random.randint(0, 255)]
                cv2.rectangle(img_select, (x, y), (x+w, y+h), color, 3)
                cv2.putText(img_select, text=str(i+1), org=(x+w//2, y+h//2), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=min(w//50,h//50), color=color, thickness=min(w//500,h//500)+1)

            self.label_img.setPhoto(img_select)
            self.ROI_select_window.my_viewer.set_img(img_select)
        else: self.data["roi"] = []


    def add_title(self):
        name = ["idx", "type", "score", "weight"]
        for i in range(len(name)):
            label = QLabel(name[i])
            self.GLayout.addWidget(label,0,i)
    
    def add_ROI_item_click(self):
        if os.path.exists("capture.jpg"):
            self.ROI_select_window.select_ROI(self.idx)
        else:
            self.alert_info_signal.emit("未拍攝照片", "請先固定好拍攝位置，再按拍攝鈕拍攝拍攝照片")


    def do_capture(self):
        # capture 
        img_name = 'capture'
        self.capture.capture(img_name, capture_num=1)

        img = cv2.imread(img_name+".jpg")
        self.img = img
        self.label_img.setPhoto(img)
        self.ROI_select_window.set_img(img)
        self.draw_ROI()
        
    def set_photo(self):
        img_name = './capture.jpg'
        if os.path.exists(img_name):
            # display img
            img = cv2.imread(img_name)
            self.label_img.setPhoto(img)
            self.img = img
            self.ROI_select_window.my_viewer.set_img(img)
            self.draw_ROI()

    def set_data(self):
        self.data["target_type"] = []
        self.data["target_score"] = []
        self.data["target_weight"] = []

        for i, roi in enumerate(self.data["roi"]):
            if len(roi)==0: continue
            self.data["target_type"].append(self.roi_info[i].target_type)
            self.data["target_score"].append(float(self.roi_info[i].target_score.text()))
            self.data["target_weight"].append(float(self.roi_info[i].target_weight.text()))

    def update_UI(self):
        self.data = self.ui.data
        self.capture = self.ui.capture
        
        self.add_title()
        self.set_photo()

        if 'target_type' in self.data and len(self.data["target_type"])>0:
            for i in range(len(self.data["target_type"])):
                self.add_ROI_item(self.data["target_type"][i], self.data["target_score"][i], self.data["target_weight"][i])
                # self.roi_info[i].type_selector.setCurrentText(self.data["target_type"][i])
                # self.roi_info[i].target_score.setText(str(self.data["target_score"][i]))
                # self.roi_info[i].target_weight.setText(str(self.data["target_weight"][i]))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = ROI_SettingPage(None)
    window.showMaximized()
    sys.exit(app.exec_()) 