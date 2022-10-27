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
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()
        self.setup_controller()

    def setup_UI(self):
        self.HLayout = QHBoxLayout(self)

        self.tree=QTreeWidget()
        self.tree.setHeaderHidden( True )
        self.tree.hide()
        self.HLayout.addWidget(self.tree)

        self.btn_toggle_open = ButtonToggleOpen()                                     
        self.HLayout.addWidget(self.btn_toggle_open)

    def update_UI(self):
        self.config = self.ui.config
        
        for k in self.config:
            root=QTreeWidgetItem(self.tree)
            root.setText(0,k)
            # root.setCheckState(0, Qt.Checked)
            self.tree.addTopLevelItem(root)
            for k2 in self.config[k]:
                child=QTreeWidgetItem()
                child.setText(0,k2)
                # child.setCheckState(0, Qt.Checked)
                root.addChild(child)

    def setup_controller(self):
        self.tree.itemClicked.connect(self.change_param_page)
        self.btn_toggle_open.clicked.connect(self.toggle_open)

    def toggle_open(self):
        if self.btn_toggle_open.isChecked():
            self.tree.hide()
            self.btn_toggle_open.setArrowType(Qt.RightArrow)
        else:
            self.tree.show()
            self.btn_toggle_open.setArrowType(Qt.LeftArrow)

    def change_param_page(self, item, col):
        if item.parent() is None: 
            if item.isExpanded():item.setExpanded(False)
            else: item.setExpanded(True)
            return

        root = item.parent().text(0)
        key = item.text(0)
        print('change param page to', root, key)
        self.param_modify_block.update_UI(root, key)
        self.param_range_block.update_UI(root, key)
        self.data["page_root"] = root
        self.data["page_key"] = key
        self.set_trigger_idx(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = ISP_Tree({})
    tree.show()
    sys.exit(app.exec_())