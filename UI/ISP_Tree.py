import sys
from PyQt5.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem, QApplication, QHBoxLayout, QPushButton, QToolButton)
from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QSize, QEasingCurve
from PyQt5.QtGui import QIcon

class ButtonToggleOpen(QToolButton):

    def __init__(self):
        super().__init__()
                             
        self.setCheckable(True)                                  
        self.setChecked(True)                                   
        self.setArrowType(Qt.RightArrow)
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        

    

class ISP_Tree(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.HLayout = QHBoxLayout(self)

        
        self.tree=QTreeWidget()
        self.tree.setHeaderHidden( True )
        root1=QTreeWidgetItem(self.tree)
        root1.setText(0,'OPE')
        self.tree.addTopLevelItem(root1)

        child1=QTreeWidgetItem()
        child1.setText(0,'WNR')
        root1.addChild(child1)

        self.HLayout.addWidget(self.tree)

        self.btn_toggle_open = ButtonToggleOpen()                                     
        self.HLayout.addWidget(self.btn_toggle_open)

        self.tree.clicked.connect(self.onClicked)
        self.btn_toggle_open.clicked.connect(self.slide_left_menu)

        self.tree.move(self.rect().width() + self.tree.width(),0)
        self.sideWidgetAnimation = QPropertyAnimation(self.tree,b"geometry")
        self.sideWidgetAnimation.setEasingCurve(QEasingCurve.InOutQuint)
        self.sideWidgetAnimation.setDuration(1000)

    def slide_left_menu(self):
        width = self.width()
        if self.btn_toggle_open.isChecked():
            self.btn_toggle_open.setArrowType(Qt.RightArrow)
            new_width=200

            self.sideWidgetAnimation.setStartValue(QRect(0-self.tree.width(),0,self.tree.width(),self.tree.height()))
            self.sideWidgetAnimation.setEndValue(QRect(0,0,self.tree.width(),self.tree.height()))
            self.sideWidgetAnimation.start()

        else:
            self.btn_toggle_open.setArrowType(Qt.LeftArrow)
            new_width=50

            self.sideWidgetAnimation.setStartValue(QRect(0,0,self.tree.width(),self.tree.height()))
            self.sideWidgetAnimation.setEndValue(QRect(0-self.tree.width(),0,self.tree.width(),self.tree.height()))
            self.sideWidgetAnimation.start()


            
        
        # self.animation = QPropertyAnimation(self, b'size')
        # self.animation.setDuration(1500)
        # self.animation.setStartValue(QSize(width, self.height()))
        # self.animation.setEndValue(QSize(new_width, self.height()))
        # self.animation.setEasingCurve(QEasingCurve.InOutQuint)
        # self.animation.start()


    def onClicked(self,qmodeLindex):
        item=self.tree.currentItem()
        print('Key=%s,value=%s'%(item.text(0),item.text(1)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = ISP_Tree({})
    tree.show()
    sys.exit(app.exec_())