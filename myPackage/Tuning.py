from PyQt5.QtWidgets import QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread

import numpy as np
from time import sleep

class Tuning(QWidget):  # 要繼承QWidget才能用pyqtSignal!!
    finish_signal = pyqtSignal()

    def __init__(self, ui, data, capture):
        super().__init__()
        self.ui = ui
        self.data = data
        self.capture = capture
        self.is_run = False

    def run(self):
        self.finish_signal.emit()

