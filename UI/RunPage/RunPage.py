from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QScrollArea
)

from .UpperPart import UpperPart
from .LowerPart import LowerPart

class RunPage(QWidget):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()
        self.setup_controller()
        
    def setup_UI(self):
        ###### parent ######
        gridLayout = QGridLayout()
        ###### parent ######

        ###### Upper Part ###### 
        self.upper_part= UpperPart(self.ui)
        gridLayout.addWidget(self.upper_part, 0, 0, 1, 1)
        ###### Upper Part ###### 

        ###### Lower Part (plot tab)###### 
        self.lower_part= LowerPart(self.ui)
        gridLayout.addWidget(self.lower_part, 1, 0, 1, 1)
        ###### Lower Part (plot tab)###### 

        #Scroll Area Properties
        scroll_wrapper = QHBoxLayout(self)
        layout_wrapper = QWidget()
        layout_wrapper.setLayout(gridLayout)
        scroll = QScrollArea() 
        scroll.setWidgetResizable(True)
        scroll.setWidget(layout_wrapper)
        scroll_wrapper.addWidget(scroll)


        ###### Set Style ###### 
        self.setStyleSheet("QLabel{font-size:12pt; font-family:微軟正黑體; color:white;}"
                          "QPushButton{font-size:12pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}")
        ###### Set Style ###### 

    def update_UI(self):
        self.data = self.ui.data
        self.config = self.ui.config

        self.upper_part.update_UI()
        self.lower_part.update_UI()

    def setup_controller(self):
        pass

    
            
            
            
