import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

        

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, dpi=80):
        self.fig = Figure(figsize=(100, 30), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class MplCanvasPlot():

    def __init__(self, label_plot):
        self.canvas = MplCanvas()
        self.layout = QHBoxLayout(label_plot)

    def update(self, data):
        self.canvas.axes.cla() # clear
        self.canvas.axes.plot(data, 's')
        self.canvas.fig.canvas.draw()  # 這裡注意是畫布重繪，self.figs.canvas
        self.canvas.fig.canvas.flush_events()  # 畫布刷新self.figs.canvas
        self.layout.addWidget(self.canvas)

class CurveSlider(QWidget):
    def __init__(self):
        super(CurveSlider, self).__init__()
        #設置標題與初始大小
        self.setWindowTitle('QSlider例子')
        self.resize(300,100)

        #垂直佈局
        Vlayout=QVBoxLayout(self)
        #創建水平方向滑動條
        self.s1=QSlider(Qt.Horizontal)
        ##設置最小值
        self.s1.setMinimum(0)
        #設置最大值
        self.s1.setMaximum(40)
        #步長
        self.s1.setSingleStep(1)
        #設置當前值
        self.s1.setValue(20)
        #刻度位置，刻度下方
        self.s1.setTickPosition(QSlider.TicksBelow)
        #設置刻度間距
        self.s1.setTickInterval(5)
        Vlayout.addWidget(self.s1)
        #設置連接信號槽函數
        self.s1.valueChanged.connect(self.valuechange)

        #創建標籤，居中
        self.label_plot = QLabel()
        plot_wraprt = QVBoxLayout()
        plot_wraprt.addWidget(self.label_plot)
        Vlayout.addLayout(plot_wraprt)

        self.canvas_plot = MplCanvasPlot(self.label_plot)
        self.canvas_plot.update(self.func(np.arange(64), self.s1.value()/2))

    def func(self, x, a):
        return (1-np.exp(-(x/a)**3.96))*0.996

    def valuechange(self):
        #輸出當前地刻度值，利用刻度值來調節字體大小
        print('current slider value=%s'%self.s1.value())
        x = np.arange(64)
        y = self.func(x, self.s1.value()/2)
        self.canvas_plot.update(y)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    demo=CurveSlider()
    demo.show()
    sys.exit(app.exec_())