from PyQt5.QtWidgets import QHBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, dpi=80):
        self.fig = Figure(figsize=(100, 30), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class MplCanvasTiming():

    def __init__(self, ui, color, label):
        self.data = []

        self.canvas = MplCanvas()
        self.layout = QHBoxLayout(ui)

        self.color = color
        self.label = label

    def reset(self):
        self.data = []
        # The new widget is deleted when its parent is deleted.
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def update(self, data):
        self.data.append(data)
        self.canvas.axes.cla()

        lines = np.array(self.data).T
        x = list(range(lines.shape[-1]))
        for i in range(lines.shape[0]):
            self.canvas.axes.plot(
                x, lines[i], color=self.color[i], label=self.label[i])
        self.canvas.axes.legend(fontsize=15)
        self.canvas.fig.canvas.draw()  # 這裡注意是畫布重繪，self.figs.canvas
        self.canvas.fig.canvas.flush_events()  # 畫布刷新self.figs.canvas
        self.layout.addWidget(self.canvas)

        if len(self.data)>=600: self.data = []
