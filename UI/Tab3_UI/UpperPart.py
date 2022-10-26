from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel
)

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer

class MyTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = 0
        self.setup_UI()

    def setup_UI(self):
        HLayout = QHBoxLayout(self)
        self.label_time = QLabel("Time")
        self.label_time.setAlignment(Qt.AlignCenter)
        self.label_time.setStyleSheet("font-family:Agency FB; font-size:30pt; width: 100%; height: 100%;")
        HLayout.addWidget(self.label_time)

        self.mytimer = QTimer(self)
        self.mytimer.timeout.connect(self.onTimer)

    def onTimer(self):
        self.counter += 1
        total_sec = self.counter
        hour = max(0, total_sec//3600)
        minute = max(0, total_sec//60 - hour * 60)
        sec = max(0, (total_sec - (hour * 3600) - (minute * 60)))
        # show time_counter (by format)
        self.label_time.setText(str(f"{hour}:{minute:0>2}:{sec:0>2}"))

    def startTimer(self):
        self.counter = -1
        self.onTimer()
        self.mytimer.start(1000)

    def stopTimer(self):
        self.mytimer.stop()

    def continueTimer(self):
        self.mytimer.start(1000)

    

class UpperPart(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_UI()

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

    def set_score(self, score):
        self.label_score.setText(score)

    def set_generation(self, gen_idx):
        self.label_generation.setText(gen_idx)

    def set_individual(self, ind_idx):
        self.label_individual.setText(ind_idx)