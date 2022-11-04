from PyQt5.QtWidgets import (
    QTabWidget, QStatusBar, QWidget, QLabel,
    QMainWindow, QMessageBox, QToolButton,
    QVBoxLayout, QScrollArea, QSplitter
)
import subprocess

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
        self.Vscroll_bar.rangeChanged.connect(self.scroll_range_changed_handler)
        self.scroll_falg = False

        self.setStyleSheet(
            """
            background-color: rgb(0, 0, 0);
            font-size:12pt; 
            font-family:微軟正黑體; 
            color:white;
            """
        )

    def show_infoes(self, info):
        print(info)
        pre_text=self.info.text()
        self.info.setText(pre_text+info+'\n')
        self.scroll_falg=True
        self.Vscroll_bar.setValue(self.Vscroll_bar.maximum())

    def scroll_range_changed_handler(self, minV, maxV):
        if self.scroll_falg:
            self.Vscroll_bar.setValue(maxV)
            self.scroll_falg=False

    def run_cmd(self, cmd, shell=False):
        """
        開啟子進程，執行對應指令，控制台打印執行過程，然後返回子進程執行的狀態碼和執行返回的數據
        :param cmd: 子進程命令
        :param shell: 是否開啟shell
        :return: 子進程狀態碼和執行結果
        """
        self.show_infoes('************** START **************')
        self.show_infoes(cmd)
        
        p = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = []
        while p.poll() is None:
            line = p.stdout.readline().strip()
            if line:
                line = _decode_data(line)
                result.append(line)
                self.show_infoes(line)
            # 清空緩存
            # sys.stdout.flush()
            # sys.stderr.flush()
        # 判斷返回碼狀態
        if p.returncode == 0:
            self.show_infoes('************** SUCCESS **************')
        else:
            self.show_infoes('************** FAILED **************')

        # return p.returncode, '\r\n'.join(result)


def _decode_data(byte_data: bytes):
    """
    解碼數據
    :param byte_data: 待解碼數據
    :return: 解碼字符串
    """
    try:
        return byte_data.decode('utf-8')
    except UnicodeDecodeError:
        return byte_data.decode('GB18030')





