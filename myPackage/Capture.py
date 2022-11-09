import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from time import sleep
from subprocess import check_output, call

import threading


class Capture(QWidget):
    capture_fail_signal = pyqtSignal()
    # logger
    log_info_signal = pyqtSignal(str)

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.CAMERA_DEBUG = False
        self.CAMERA_PATH = '/sdcard/DCIM/Camera/'
        self.state = threading.Condition()

    def capture(self, path = "", focus_time = 4, save_time = 1, capture_num = 1):

        self.open_camera()
        sleep(focus_time) #wait fot auto focus
        # capture
        for i in range(capture_num):
            self.press_camera_button()
            sleep(0.01) 
        sleep(save_time) #wait for save photo
        self.transfer_img(path, capture_num)

    def open_camera(self):
        self.log_info_signal.emit('\nopen_camera')
        rc, r = self.logger.run_cmd("adb shell am start -a android.media.action.STILL_IMAGE_CAMERA --ez com.google.assistant.extra.CAMERA_OPEN_ONLY true --ez android.intent.extra.CAMERA_OPEN_ONLY true --ez isVoiceQuery true --ez NoUiQuery true --es android.intent.extra.REFERRER_NAME android-app://com.google.android.googlequicksearchbox/https/www.google.com")
        # if rc!=0: return False

    def clear_camera_folder(self):
        #delete from phone: adb shell rm self.CAMERA_PATH/*
        self.log_info_signal.emit('\nclear_camera_folder')
        rc, r = self.logger.run_cmd("adb shell rm -rf {} *".format(self.CAMERA_PATH))
        # if rc!=0: return

    def press_camera_button(self):
        #condition 1 screen on 2 camera open: adb shell input keyevent = CAMERA
        self.log_info_signal.emit('\npress_camera_button')
        rc, r = self.logger.run_cmd("adb shell input keyevent = CAMERA")
        # if rc!=0: return

    def transfer_img(self, path='', capture_num = 1):
        self.log_info_signal.emit("\ntransfer_img")
        # list all file
        rc, r = self.logger.run_cmd("adb shell ls -lt {}".format(self.CAMERA_PATH))
        if rc!=0: return

        # find the last num
        file_names = r.split('\n')[1:capture_num+1] 
        file_names = [f.split(' ')[-1][:-1] for f in file_names]
        self.log_info_signal.emit('file_names')
        self.log_info_signal.emit("{}".format(file_names))
        if file_names[0] == '':
            self.capture_fail()
            self.log_info_signal.emit('正在重新拍攝...')
            self.capture(path=path, capture_num=capture_num)

        else:
            for i in range(capture_num):
                file_name = self.CAMERA_PATH + file_names[i]
                if path == "":
                    p = 'test/'+file_name.split('/')[-1]
                elif capture_num==1:
                    p = str(path+".jpg")
                else:
                    p = str(path+"_"+str(i)+".jpg")
                self.log_info_signal.emit('transfer {} to {}'.format(file_name, p))
                self.logger.run_cmd("adb pull {} {}".format(file_name, p))

    def capture_fail(self):
        self.capture_fail_signal.emit()
        self.state.acquire()
        self.state.wait()
        self.state.release()



