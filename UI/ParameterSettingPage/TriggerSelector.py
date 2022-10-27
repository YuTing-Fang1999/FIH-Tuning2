from PyQt5.QtWidgets import QComboBox

class TriggerSelector(QComboBox):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setup_UI()

    def setup_UI(self):
        self.setStyleSheet("font-size:12pt; font-family:微軟正黑體; background-color: rgb(255, 255, 255);")

    def update_UI(self, aec_trigger_datas):
        self.data = self.ui.data
        item_names = ["lux_idx from {} to {},  gain from {} to {}".format(d[0], d[1], d[2], d[3])for d in aec_trigger_datas]
        self.clear()
        self.addItems(item_names)