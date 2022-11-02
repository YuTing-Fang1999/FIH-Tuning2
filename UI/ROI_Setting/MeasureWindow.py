from PyQt5.QtWidgets import (
    QWidget, QSpacerItem, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,
    QPushButton, QLabel, QApplication, QCheckBox
)    
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

import sys
sys.path.append("../..")

from ImageViewer import ImageViewer
from myPackage.Tuning.ImageMeasurement import *


class Score(QWidget):
    def __init__(self, name, tip):
        super().__init__()  
        
        gridLayout = QGridLayout(self)
        gridLayout.setAlignment(Qt.AlignCenter)

        self.label_score = []
        self.check_box=[]
        for j in range(len(name)):
            check_box = QCheckBox()
            self.check_box.append(check_box)
            gridLayout.addWidget(check_box, j, 0)

            label = QLabel(name[j])
            label.setToolTip(tip[j])
            gridLayout.addWidget(label, j, 1)

            label = QLabel()
            self.label_score.append(label)
            gridLayout.addWidget(label, j, 2)

class Block(QWidget):
    def __init__(self, name, tip):
        super().__init__()  

        self.VLayout = QVBoxLayout(self)

        self.img_block = ImageViewer()
        self.img_block.setAlignment(Qt.AlignCenter)
        self.VLayout.addWidget(self.img_block)

        self.score_block = Score(name, tip)
        self.VLayout.addWidget(self.score_block)

class MeasureWindow(QWidget):  
    to_main_window_signal = pyqtSignal(int, list, list, list)
    
    def __init__(self):
        super().__init__()  
        self.setup_UI()

        self.calFunc = {}
        self.calFunc["sharpness"] = get_sharpness
        self.calFunc["chroma stdev"] = get_chroma_stdev
        self.calFunc["luma stdev"] = get_luma_stdev

        self.type_name = ["sharpness", "chroma stdev", "luma stdev"]

    def setup_UI(self):
        self.resize(800, 600)

        
        self.name = ["luma noise", "chroma noise", "sharpness"]
        tip = [
            "噪聲\n方法取自J. Immerkær, “Fast Noise Variance Estimation”這篇論文",
            "",
            ""
        ]

        self.VLayout = QVBoxLayout(self)
        self.VLayout.setAlignment(Qt.AlignCenter)
        self.VLayout.setContentsMargins(50, 50, 50, 50)

        HLayout = QHBoxLayout()
        self.block = Block(self.name, tip)
        HLayout.addWidget(self.block)
        self.VLayout.addLayout(HLayout)

        
        self.btn_OK = QPushButton("OK")
        self.VLayout.addWidget(self.btn_OK)
        self.btn_OK.clicked.connect(lambda: self.btn_ok_function())


        self.setStyleSheet(
            "QLabel{font-size:12pt; font-family:微軟正黑體;}"
            "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}"
        )

    def measure_target(self, img_idx, my_x_y_w_h, target_roi_img):
        self.img_idx = img_idx
        self.my_x_y_w_h = my_x_y_w_h
        self.block.img_block.setPhoto(target_roi_img)

        self.score_value = []
        for i in range(3):
            v = self.calFunc[self.type_name[i]](target_roi_img)
            v = np.around(v, 5)
            self.block.score_block.label_score[i].setText(str(v))
            self.score_value.append(v)

        self.showMaximized()

    def btn_ok_function(self):
        target_type = []
        score_value = []
        for i in range(3):
            if self.block.score_block.check_box[i].isChecked():
                target_type.append(self.type_name[i])
                score_value.append(self.score_value[i])

        self.close()
        self.to_main_window_signal.emit(self.img_idx, self.my_x_y_w_h, target_type, score_value)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MeasureWindow()
    window.show()
    sys.exit(app.exec_())