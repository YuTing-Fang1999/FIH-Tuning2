import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from time import sleep
from subprocess import check_output, call

import threading


class Capture(QWidget):
    capture_fail_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.CAMERA_DEBUG = True
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
        os.system("adb shell am start -a android.media.action.STILL_IMAGE_CAMERA --ez com.google.assistant.extra.CAMERA_OPEN_ONLY true --ez android.intent.extra.CAMERA_OPEN_ONLY true --ez isVoiceQuery true --ez NoUiQuery true --es android.intent.extra.REFERRER_NAME android-app://com.google.android.googlequicksearchbox/https/www.google.com")

                
    def clear_camera_folder(self):
        #delete from phone: adb shell rm self.CAMERA_PATH/*
        if self.CAMERA_DEBUG: print('clear_camera_folder')
        r = check_output(['adb','shell','rm','-rf',self.CAMERA_PATH + '*'])
        if self.CAMERA_DEBUG: print(r.strip())

    def press_camera_button(self):
        #condition 1 screen on 2 camera open: adb shell input keyevent = CAMERA
        if self.CAMERA_DEBUG: print('press_camera_button')
        call(['adb','shell','input','keyevent = CAMERA'])
        
    def transfer_img(self, path='', capture_num = 1):
        if self.CAMERA_DEBUG: print('screen transfer_img')
        # list all file
        r = check_output(['adb','shell','ls','-lt', self.CAMERA_PATH])
        if self.CAMERA_DEBUG: print('all files\n',r.decode('utf-8'))

        # find the last num
        file_names = r.decode('utf-8').split('\n')[1:capture_num+1] 
        file_names = [f.split(' ')[-1][:-1] for f in file_names]
        # print(file_names)

        if file_names[0] == '':
            self.capture_fail()
            print('正在重新拍攝...')
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
                print('transfer',file_name,'to',p)
                r = check_output(['adb','pull', file_name, p])
                if self.CAMERA_DEBUG: print(r.strip())

    def capture_fail(self):
        self.capture_fail_signal.emit()
        self.state.acquire()
        self.state.wait()
        self.state.release()



