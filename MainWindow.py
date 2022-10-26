import sys
from PyQt5.QtWidgets import (
    QTabWidget, QStatusBar,
    QMainWindow, QApplication,
    QLabel, QCheckBox, QComboBox, QListWidget, QLineEdit,
    QLineEdit, QSpinBox, QDoubleSpinBox, QSlider, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

from UI.Tab1_UI.Tab1 import Tab1
from UI.Tab2_UI.Tab2 import Tab2
from UI.Tab3_UI.Tab3 import Tab3
from myPackage.Setting import Setting
from myPackage.Tuning.Tuning import Tuning
from myPackage.Capture import Capture
from myPackage.Param_window import Param_window

import json
import threading
import ctypes, inspect

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.config = self.read_config()
        self.setting = Setting(self)
        self.data = self.setting.data
        self.capture = Capture()
        self.setup_UI()
        
        self.tuning = Tuning(self, self.data, self.config, self.capture)
        self.setup_controller()
        

        

    def setup_UI(self):
        self.setWindowTitle("FIH-Tuning")
        self.param_window = Param_window()
        
        self.tabWidget = QTabWidget()

        self.tab1 = Tab1(self.data, self.capture)
        self.tab2 = Tab2(self.data, self.config)
        self.tab3 = Tab3(self.data, self.config)

        self.tabWidget.addTab(self.tab1, "選擇project")
        self.tabWidget.addTab(self.tab2, "參數設定")
        self.tabWidget.addTab(self.tab3, "執行")

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

    def setup_controller(self):
        self.tab1.project_setting.set_project_signal.connect(self.tab2.set_project)
        self.tab3.upper_part.btn_run.clicked.connect(self.run)
        self.tab3.upper_part.btn_param_window.clicked.connect(self.show_param_window)

        self.capture.capture_fail_signal.connect(self.capture_fail)
        self.setting.alert_info_signal.connect(self.alert_info)
        
        # tuning to UI
        self.tuning.finish_signal.connect(self.finish)
        self.tuning.set_score_signal.connect(self.tab3.upper_part.set_score)
        self.tuning.set_generation_signal.connect(self.tab3.upper_part.set_generation)
        self.tuning.set_individual_signal.connect(self.tab3.upper_part.set_individual)
        # tuning to param window
        self.tuning.update_param_window_signal.connect(self.update_param_window)
        self.tuning.setup_param_window_signal.connect(self.setup_param_window)

    def read_config(self):
        with open('config.json') as f:
            return json.load(f)

    def start(self):
        # 更新設定的參數
        if not self.setting.set_data(): return

        self.tuning.is_run = True
        self.tab3.upper_part.btn_run.setText('STOP')
        self.tab3.upper_part.mytimer.startTimer()

        # show info
        self.tab3.lower_part.tab_info.label.setAlignment(Qt.AlignLeft)
        self.tab3.lower_part.tab_info.label.setText(
            json.dumps(self.data, indent=2) + '\n' +
            json.dumps(self.config[self.data["page_root"]][self.data["page_key"]], indent=2)
        )

        # 建立一個子執行緒
        self.tuning_task = threading.Thread(target=lambda: self.tuning.run())
        # 當主程序退出，該執行緒也會跟著結束
        self.tuning_task.daemon = True
        # 執行該子執行緒
        self.tuning_task.start()


    def finish(self):
        self.tuning.is_run = False
        self.tab3.upper_part.btn_run.setText('Run')
        self.tab3.upper_part.mytimer.stopTimer()

    def run(self):
        if self.tuning.is_run:
            print("STOP")
            self.finish()
            stop_thread(self.tuning_task)

        else:
            print("Run")
            self.start()

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


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
def stop_thread(thread):
    """
    @profile:強制停掉線程函數
    :param thread:
    :return:
    """
    if thread == None:
        print('thread id is None, return....')
        return
    _async_raise(thread.ident, SystemExit)
