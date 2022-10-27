from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel
)

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from .MyTimer import MyTimer

import threading
import ctypes, inspect
import json

class UpperPart(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        horizontalLayout = QHBoxLayout(self)

        self.btn_run = QPushButton("Run")
        self.btn_run.setStyleSheet("font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        horizontalLayout.addWidget(self.btn_run)

        self.btn_param_window = QPushButton("Param")
        self.btn_param_window.setStyleSheet("font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        horizontalLayout.addWidget(self.btn_param_window)

        label = QLabel("總分")
        label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        horizontalLayout.addWidget(label)

        self.label_score = QLabel("#")
        horizontalLayout.addWidget(self.label_score)

        gridLayout_gen = QGridLayout()

        label = QLabel("generation:")
        gridLayout_gen.addWidget(label, 0, 0, 1, 1)

        label = QLabel("individual:")
        gridLayout_gen.addWidget(label, 1, 0, 1, 1)

        self.label_generation = QLabel("#")
        gridLayout_gen.addWidget(self.label_generation, 0, 1, 1, 1)

        self.label_individual = QLabel("#")
        gridLayout_gen.addWidget(self.label_individual, 1, 1, 1, 1)
        horizontalLayout.addLayout(gridLayout_gen)

        self.mytimer = MyTimer()
        horizontalLayout.addWidget(self.mytimer)

    def update_UI(self):
        self.tuning = self.ui.tuning
        self.setting = self.ui.setting
        self.data = self.ui.data
        self.config = self.ui.config

    def setup_controller(self):
        self.btn_run.clicked.connect(self.run)
        self.btn_param_window.clicked.connect(self.show_param_window)

    def set_score(self, score):
        self.label_score.setText(score)

    def set_generation(self, gen_idx):
        self.label_generation.setText(gen_idx)

    def set_individual(self, ind_idx):
        self.label_individual.setText(ind_idx)

    def run(self):
        print('click run btn')
        if self.tuning.is_run:
            print("STOP")
            self.finish()
            stop_thread(self.tuning_task)

        else:
            print("Run")
            self.start()

    def start(self):
        if not self.setting.set_data(): return

        self.tuning.is_run = True
        self.btn_run.setText('STOP')
        self.mytimer.startTimer()

        # show info
        self.ui.run_page.lower_part.tab_info.label.setAlignment(Qt.AlignLeft)
        self.ui.run_page.lower_part.tab_info.label.setText(
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
        self.btn_run.setText('Run')
        self.mytimer.stopTimer()

    def show_param_window(self):
        self.ui.param_window.showNormal()

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

    

    