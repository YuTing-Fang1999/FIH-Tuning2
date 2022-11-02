from PyQt5.QtWidgets import QPushButton, QWidget, QComboBox, QLineEdit, QLabel

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

    def __init__(self, table, region_id, idx, target_type, target_score, target_weight):
        super().__init__()
        self.table = table
        self.region_id = region_id
        self.idx = idx
        self.target_type = target_type
        self.score_value = target_score
        self.target_weight = target_weight

        #Create widget
        # self.type_selector = Score_type_selector()
        self.type_selector = QLabel(target_type)

        self.target_score = QLineEdit()
        self.target_score.setText(str(target_score))

        self.target_weight = QLineEdit()
        self.target_weight.setText(str(target_weight))

        self.btn_delete = QPushButton("刪除")
        self.btn_delete.clicked.connect(self.delete_row)

    def delete_row(self):
        print("delete row", self.idx)
        self.table.removeRow(self.idx)




    