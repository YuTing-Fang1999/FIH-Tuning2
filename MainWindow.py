import sys
from PyQt5.QtWidgets import (
    QTabWidget, QStatusBar,
    QMainWindow, QApplication,
    QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

from UI.ProjectSetting.ProjectSettingPage import ProjectSettingPage
from UI.ROI_Setting.ROI_SettingPage import ROI_SettingPage
from UI.ParameterSettingPage.ParameterSettingPage import ParameterSettingPage
from UI.RunPage.RunPage import RunPage
from myPackage.Setting import Setting
from myPackage.Tuning.Tuning import Tuning
from myPackage.Capture import Capture
from myPackage.Param_window import Param_window

import json


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_UI()
        self.config = self.read_config()
        self.setting = Setting(self)
        self.data = self.setting.data
        self.capture = Capture()
        self.tuning = Tuning(self.run_page.lower_part, self.data, self.config, self.capture)
        self.update_UI()
        # self.setup_controller()
        
    def setup_UI(self):
        self.setWindowTitle("FIH-Tuning")
        self.param_window = Param_window()
        
        self.tabWidget = QTabWidget()

        self.project_setting_page = ProjectSettingPage(self)
        self.ROI_setting_page = ROI_SettingPage(self)
        self.parameter_setting_page = ParameterSettingPage(self)
        self.run_page = RunPage(self)

        self.tabWidget.addTab(self.project_setting_page, "選擇project")
        self.tabWidget.addTab(self.ROI_setting_page, "ROI設定")
        self.tabWidget.addTab(self.parameter_setting_page, "參數設定")
        self.tabWidget.addTab(self.run_page, "執行")

        self.setCentralWidget(self.tabWidget)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setStyleSheet("color: white")
        self.statusbar.showMessage('只存在3秒的消息', 3000)

        self.setStyleSheet(
            """
            * {
                background-color: rgb(124, 124, 124);
            }
            
            QMessageBox QLabel {
                font-size:12pt; font-family:微軟正黑體; color:white;
            }

            QMessageBox QPushButton{
                font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);
            }
            """

        )

    def update_UI(self):
        self.project_setting_page.update_UI()
        self.ROI_setting_page.update_UI()
        self.parameter_setting_page.update_UI()
        self.run_page.update_UI()

    def setup_controller(self):
        pass
        # self.tab1.project_setting_block.set_project_signal.connect(self.tab2.set_project)
        # self.tab3.upper_part.btn_run.clicked.connect(self.run)
        # self.tab3.upper_part.btn_param_window.clicked.connect(self.show_param_window)

        # self.capture.capture_fail_signal.connect(self.capture_fail)
        # self.setting.alert_info_signal.connect(self.alert_info)
        
        # # tuning to UI
        # self.tuning.finish_signal.connect(self.finish)
        # self.tuning.set_score_signal.connect(self.tab3.upper_part.set_score)
        # self.tuning.set_generation_signal.connect(self.tab3.upper_part.set_generation)
        # self.tuning.set_individual_signal.connect(self.tab3.upper_part.set_individual)
        # # tuning to param window
        # self.tuning.update_param_window_signal.connect(self.update_param_window)
        # self.tuning.setup_param_window_signal.connect(self.setup_param_window)

    def read_config(self):
        with open('config.json') as f:
            return json.load(f)

    def capture_fail(self):
        self.tab3.upper_part.mytimer.stopTimer()
        QMessageBox.about(self, "拍攝未成功", "拍攝未成功\n請多按幾次拍照鍵測試\n再按ok鍵重新拍攝")
        self.capture.state.acquire()
        self.capture.state.notify()  # Unblock self if waiting.
        self.capture.state.release()
        self.tab3.upper_part.mytimer.continueTimer()

    def alert_info(self, title, text):
        QMessageBox.about(self, title, text)

    def closeEvent(self, event):
        print('window close')
        self.setting.write_setting()

    def set_statusbar(self, text):
        self.statusbar.showMessage(text, 5000)

    ##### param_window #####
    def show_param_window(self):
        self.param_window.showNormal()
    
    def setup_param_window(self, popsize, param_change_num, IQM_names):
        self.param_window.setup(popsize=popsize, param_change_num=param_change_num, IQM_names=IQM_names)

    def update_param_window(self, idx, param_value, score, IQM):
        self.param_window.update(idx, param_value, score, IQM)
    ##### param_window #####



