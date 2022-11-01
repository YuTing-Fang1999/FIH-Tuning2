from tkinter.messagebox import NO
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np

from myPackage.Tuning.ImageMeasurement import *
from .ImageViewer import ImageViewer as DisplayImage
class ROI_coordinate(object):
    r1 = -1
    r2 = -1
    c1 = -1
    c2 = -1


class ImageViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        # 設置view可以進行鼠標的拖拽選擇
        self.setDragMode(self.RubberBandDrag)

        # self.roi_coordinate = ROI_coordinate()  # 圖片座標
        self.origin_pos = None  # 螢幕座標
        self.end_pos = None
        self.scenePos1 = None
        self.scenePos2 = None

        self.img = []


    def hasPhoto(self):
        return not self._empty

    def resizeEvent(self, event):
        self.fitInView()

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        # self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self._photo.setPixmap(QtGui.QPixmap())
        # self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def mousePressEvent(self, event):
        super(ImageViewer, self).mousePressEvent(event)
        if self.dragMode() == self.RubberBandDrag:
            # if event.buttons() == Qt.LeftButton:
            self.origin_pos = event.pos()
            

    def mouseReleaseEvent(self, event):
        super(ImageViewer, self).mouseReleaseEvent(event)
        if self.dragMode() == self.RubberBandDrag:
            # if event.buttons() == Qt.LeftButton:
            self.end_pos = event.pos()
            # print(self.origin_pos.x(), self.origin_pos.y())

            self.set_ROI_draw()

    def set_ROI_draw(self):

        img = self.img.copy()
        r1 = 0
        c1 = 0
        r2 = img.shape[0]
        c2 = img.shape[1]

        if self.origin_pos != None:
            # print(self.origin_pos)
            # print(self.end_pos)
            self.scenePos1 = self.mapToScene(self.origin_pos).toPoint()
            c1 = max(0, self.scenePos1.x())
            r1 = max(0, self.scenePos1.y())

            self.scenePos2 = self.mapToScene(self.end_pos).toPoint()
            c2 = min(img.shape[1], self.scenePos2.x())
            r2 = min(img.shape[0], self.scenePos2.y())
            # print(r1,r2,c1,c2)
            if r2-r1<2 or c2-c1<2:
                r1 = 0
                c1 = 0
                r2 = img.shape[0]
                c2 = img.shape[1]

        cv2.rectangle(img, (c1, r1), (c2, r2), (0, 0, 255), 5)

        qimg = QImage(img, img.shape[1], img.shape[0], img.shape[1]
                        * img.shape[2], QImage.Format_RGB888).rgbSwapped()
        self.setPhoto(QPixmap(qimg))


class MeasureTargetWindow(QtWidgets.QWidget):
    to_main_window_signal = pyqtSignal(int, float)

    def __init__(self):
        super().__init__()
        self.filefolder = "./"
        self.tab_idx = -1
        self.filename = ""

        self.calFunc = {}
        self.calFunc["sharpness"] = get_sharpness
        self.calFunc["chroma stdev"] = get_chroma_stdev
        self.calFunc["luma stdev"] = get_luma_stdev

        # Widgets
        self.display = DisplayImage(self)
        self.viewer = ImageViewer(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText('按下Ctrl可以使用滑鼠縮放拖曳\n滑鼠點擊可選擇整張照片')
        self.btn_OK = QtWidgets.QPushButton(self)
        self.btn_OK.setText("OK")
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        HBlayout = QtWidgets.QHBoxLayout()

        HBlayout.addWidget(self.display)
        HBlayout.addWidget(self.viewer)

        VBlayout.addWidget(self.label)
        VBlayout.addLayout(HBlayout)
        VBlayout.addWidget(self.btn_OK)

        # # 接受信號後要連接到什麼函數(將值傳到什麼函數)
        self.btn_OK.clicked.connect(
            lambda: self.get_roi_coordinate(self.viewer.img)
        )

        self.setStyleSheet(
            "QWidget{background-color: rgb(66, 66, 66);}"
            "QLabel{font-size:20pt; font-family:微軟正黑體; color:white;}"
            "QPushButton{font-size:20pt; font-family:微軟正黑體; background-color:rgb(255, 170, 0);}")

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.viewer.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.viewer.setDragMode(self.viewer.RubberBandDrag)

    def open_img(self):
        filepath, filetype = QFileDialog.getOpenFileName(self,
                                                         "選擇target照片",
                                                         self.filefolder,  # start path
                                                         'Image Files(*.png *.jpg *.jpeg *.bmp)')

        if filepath == '':
            return

        # filepath = '../test img/grid2.jpg'
        self.filefolder = '/'.join(filepath.split('/')[:-1])
        self.filename = filepath.split('/')[-1]

        
        # load img
        img = cv2.imdecode(np.fromfile(file=filepath, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.set_img(img)

        # self.show()

    def measure_target(self, img_idx, target_type):
        self.tab_idx = img_idx
        self.target_type = target_type
        
        if len(self.viewer.img)==0: self.open_img()
        self.viewer.set_ROI_draw()
        self.showMaximized()

    def set_img(self, img):
        self.viewer.img = img
        qimg = QImage(img, img.shape[1], img.shape[0], img.shape[1] * img.shape[2], QImage.Format_RGB888).rgbSwapped()

        self.viewer.setPhoto(QPixmap(qimg))
        self.viewer.fitInView()

        # self.viewer.set_ROI_draw()
        # self.showMaximized()

    def get_roi_coordinate(self, img):
        # roi_img = self.viewer.img[int(roi_coordinate.r1):int(roi_coordinate.r2), int(roi_coordinate.c1):int(roi_coordinate.c2)]
        # cv2.imshow('roi_img', roi_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        roi_coor = ROI_coordinate()

        if self.viewer.scenePos1 == None:

            roi_coor.r1 = 0
            roi_coor.c1 = 0
            roi_coor.r2 = img.shape[0]
            roi_coor.c2 = img.shape[1]

        else:

            self.viewer.fitInView()
            self.viewer.origin_pos = self.viewer.mapFromScene(self.viewer.scenePos1)
            self.viewer.end_pos = self.viewer.mapFromScene(self.viewer.scenePos2)

            # fitInView 要重新生座標才不會有誤差
            self.viewer.scenePos1 = self.viewer.mapToScene(self.viewer.origin_pos).toPoint()
            c1 = max(0, self.viewer.scenePos1.x())
            r1 = max(0, self.viewer.scenePos1.y())

            self.viewer.scenePos2 = self.viewer.mapToScene(self.viewer.end_pos).toPoint()
            c2 = min(img.shape[1], self.viewer.scenePos2.x())
            r2 = min(img.shape[0], self.viewer.scenePos2.y())

            if r2-r1<2 or c2-c1<2:
                r1 = 0
                c1 = 0
                r2 = img.shape[0]
                c2 = img.shape[1]

            roi_coor.r1 = r1
            roi_coor.c1 = c1
            roi_coor.r2 = r2
            roi_coor.c2 = c2

        print(roi_coor.r1, roi_coor.r2, roi_coor.c1, roi_coor.c2)
        ROI_img = img[roi_coor.r1:roi_coor.r2, roi_coor.c1:roi_coor.c2]
        print(ROI_img.shape)
        score = self.calFunc[self.target_type](ROI_img)

        self.close()
        self.to_main_window_signal.emit(self.tab_idx, np.around(score,5))
        

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MeasureTargetWindow()
    window.open_img(0)
    sys.exit(app.exec_())
