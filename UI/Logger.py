from PyQt5.QtWidgets import (
    QTabWidget, QStatusBar, QWidget, QLabel,
    QMainWindow, QMessageBox, QToolButton,
    QVBoxLayout, QScrollArea, QSplitter
)

class Logger(QWidget):
    def __init__(self):
        super().__init__()
        VLayout = QVBoxLayout(self)
        self.info = QLabel("logger\n\n")
        
        #Scroll Area Properties
        scroll = QScrollArea() 
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.info)
        VLayout.addWidget(scroll)

        self.Vscroll_bar = scroll.verticalScrollBar()
        self.Vscroll_bar.rangeChanged.connect(self.ran)
        self.scroll_falg = False

        self.setStyleSheet(
            """
            background-color: rgb(0, 0, 0);
            font-size:12pt; 
            font-family:微軟正黑體; 
            color:white;
            """
        )

    def show_infoes(self,info):
        print(info)
        pre_text=self.info.text()
        self.info.setText(pre_text+info+'\n')
        self.scroll_falg=True
        self.Vscroll_bar.setValue(self.Vscroll_bar.maximum())

    def ran(self, minV, maxV):
        if self.scroll_falg:
            self.Vscroll_bar.setValue(maxV)
            self.scroll_falg=False




