from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np

from UI.ROI_Setting.ROI_Info import ROI_Info
from .ImageViewer import ImageViewer
from .ROI_Select_Window import ROI_Select_Window
import os
import random

class ROI_SettingPage(QtWidgets.QWidget):
    to_setting_signal = pyqtSignal(list, list, list)
    alert_info_signal = pyqtSignal(str, str)

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.idx=0
        self.roi_info = []

        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        # Widgets
        self.label_img = ImageViewer()
        self.label_img.setAlignment(QtCore.Qt.AlignCenter)
        self.label_img.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.ROI_select_window = ROI_Select_Window()
        self.measure_target_window = ROI_Select_Window()

        # Arrange layout
        self.btn_capture = QtWidgets.QPushButton()
        self.btn_capture.setText("拍攝照片")
        self.btn_capture.setToolTip("會拍攝一張照片，請耐心等候")

        self.btn_add_ROI_item = QtWidgets.QPushButton()
        self.btn_add_ROI_item.setText("增加區域")
        self.btn_add_ROI_item.setToolTip("按下後會新增一個目標區域")

        self.GLayout = QtWidgets.QGridLayout()
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # Arrange layout
        HBlayout = QtWidgets.QHBoxLayout(self)

        VBlayout = QtWidgets.QVBoxLayout()
        VBlayout.addWidget(self.label_img)
        VBlayout.addWidget(self.btn_capture)
        VBlayout.addWidget(self.btn_add_ROI_item)
        HBlayout.addLayout(VBlayout)

        VBlayout = QtWidgets.QVBoxLayout()
        VBlayout.addLayout(self.GLayout)
        VBlayout.addItem(spacerItem)
        HBlayout.addLayout(VBlayout)

        HBlayout.setStretch(0,3)
        HBlayout.setStretch(1,2)


        self.setStyleSheet(
            "QWidget{background-color: rgb(66, 66, 66);}"
            "QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
            "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
            "QLineEdit{font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255); border: 2px solid gray; border-radius: 5px;}")

    def setup_controller(self):
        self.ROI_select_window.to_main_window_signal.connect(self.set_roi_coordinate)
        self.measure_target_window.to_main_window_signal.connect(self.set_target_score)
        self.btn_add_ROI_item.clicked.connect(self.add_ROI_item_click)
        self.btn_capture.clicked.connect(self.do_capture)
        
    def set_roi_coordinate(self, img_idx, img, roi_coordinate, filename):
        self.add_ROI_item()
        # print(roi_coordinate)
        x, y, w, h = roi_coordinate.c1, roi_coordinate.r1, (roi_coordinate.c2-roi_coordinate.c1), (roi_coordinate.r2-roi_coordinate.r1)
        self.data["roi"][img_idx-1]=[x, y, w, h]
        self.draw_ROI()

    def set_target_score(self, img_idx, score):
        self.roi_info[img_idx-1].target_score.setText(str(score))
        

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
            self.ROI_select_window.set_img(img_select)
            self.measure_target_window.my_viewer.set_img(img_select)
        else: self.data["roi"] = []


    def add_title(self):
        name = ["idx", "type", "score", "weight"]
        for i in range(len(name)):
            self.label = QtWidgets.QLabel()
            self.label.setText(name[i])
            self.GLayout.addWidget(self.label,0,i)

    def add_ROI_item(self):
        self.idx+=1

        label = QtWidgets.QLabel()
        label.setText(str(self.idx))
        self.GLayout.addWidget(label, self.idx, 0)

        roi_info = ROI_Info(self.idx, self.ROI_select_window, self.measure_target_window)

        self.GLayout.addWidget(roi_info.type_selector,self.idx,1)
        self.GLayout.addWidget(roi_info.target_score,self.idx,2)
        self.GLayout.addWidget(roi_info.target_weight,self.idx,3)
        self.GLayout.addWidget(roi_info.btn_selectROI,self.idx,4)
        self.GLayout.addWidget(roi_info.btn_measure,self.idx,5)

        self.roi_info.append(roi_info)

        if len(self.data["roi"]) < self.idx:
            self.data["roi"].append([])

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
            self.ROI_select_window.set_img(img)
            self.draw_ROI()

    def set_data(self):
        self.data["target_type"] = []
        self.data["target_score"] = []
        self.data["target_weight"] = []

        for i, roi in enumerate(self.data["roi"]):
            if len(roi)==0: continue
            self.data["target_type"].append(self.roi_info[i].type_selector.type)
            self.data["target_score"].append(float(self.roi_info[i].target_score.text()))
            self.data["target_weight"].append(float(self.roi_info[i].target_weight.text()))

    def update_UI(self):
        self.data = self.ui.data
        self.capture = self.ui.capture
        
        self.add_title()
        self.set_photo()

        if 'target_type' in self.data and len(self.data["target_type"])>0:
            for i in range(len(self.data["target_type"])):
                self.add_ROI_item()
                self.roi_info[i].type_selector.setCurrentText(self.data["target_type"][i])
                self.roi_info[i].target_score.setText(str(self.data["target_score"][i]))
                self.roi_info[i].target_weight.setText(str(self.data["target_weight"][i]))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ROI_SettingPage()
    window.showMaximized()
    sys.exit(app.exec_()) 