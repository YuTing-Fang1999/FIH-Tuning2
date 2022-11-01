from PyQt5.QtWidgets import QPushButton, QWidget, QComboBox, QLineEdit

class Score_type_selector(QComboBox):
    def __init__(self):
        super(Score_type_selector, self).__init__()

        self.addItems(['sharpness', 'chroma stdev', 'luma stdev'])
        self.type='sharpness'

        #Create widget
        self.setStyleSheet("background-color: rgb(255, 255, 255); font-size:12pt; font-family:微軟正黑體;")

        self.currentIndexChanged[str].connect(self.set_type)

    def set_type(self,type):
        self.type=type
        # print(self.type)


class ROI_Info(QWidget):

    def __init__(self, idx, w1, w2):
        super().__init__()
        self.idx = idx
        self.w1=w1
        self.w2=w2

        #Create widget
        self.type_selector = Score_type_selector()

        self.target_score = QLineEdit()
        self.target_score.setText("0")

        self.target_weight = QLineEdit()
        self.target_weight.setText("1")

        self.btn_selectROI = QPushButton("選擇ROI")
        self.btn_measure = QPushButton("計算分數")

        self.btn_selectROI.clicked.connect(self.btn_selectROI_click)
        self.btn_measure.clicked.connect(self.btn_measure_click)

    def set_pos(self, origin_pos, end_pos):
        self.origin_pos = origin_pos
        self.end_pos = end_pos

    def btn_selectROI_click(self):
         self.w1.select_ROI(self.idx)

    def btn_measure_click(self):
         self.w2.measure_target(self.idx, self.type_selector.type, self.origin_pos, self.end_pos)

    