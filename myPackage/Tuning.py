# Pytorch
import torch
import torch.nn as nn

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from scipy import stats  # zcore
from scipy.signal import convolve2d
import cv2

import os
import sys
import threading
from subprocess import check_output, call
from time import sleep
import math
import numpy as np

import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread

import matplotlib
matplotlib.use('Qt5Agg')

from .ML import ML 

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, dpi=80):
        self.fig = Figure(figsize=(100, 30), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class MplCanvas_timing():

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

class HyperOptimizer():
    def __init__(self, init_value, final_value, method, rate=0, decay_value=0):
        self.init_value = init_value
        self.final_value = final_value

        self.decay_value = decay_value
        self.rate = rate

        if method == "step":
            self.method = self.step_decay
        if method == "exponantial":
            self.method = self.exponantial_decay
        if method == "exponantial_reverse":
            self.method = self.exponantial_reverse
        if method == "constant":
            self.method = self.constant

    def constant(self, generation):
        return self.init_value

    def step_decay(self, generation):
        v = self.init_value - self.decay_value * generation
        return v

    def exponantial_decay(self, generation):
        # if generation % 15 == 0: 
        #     self.init_value+=0.1
            # self.final_value-=0.1

        v = (self.init_value-self.final_value) * \
            np.exp(-self.rate * (generation % 15)) + self.final_value

        return v

    def exponantial_reverse(self, generation):
        # if generation % 15 == 0: 
        #     self.init_value+=0.1
        #     self.rate-=0.01

        v = self.init_value + (self.rate*(generation % 15))**np.exp(0.5)
        
        return min(v, self.final_value)

    def update(self, generation):
        return self.method(generation)


class Tuning(QWidget):  # 要繼承QWidget才能用pyqtSignal!!
    show_param_window_signal = pyqtSignal()
    setup_param_window_signal = pyqtSignal(int, int, np.ndarray) # popsize, param_change_num, IQM_names
    update_param_window_signal = pyqtSignal(int, np.ndarray, float, np.ndarray)

    def __init__(self, ui, setting, capture):
        super().__init__()
        self.ML = None

        self.ui = ui
        self.setting = setting
        self.capture = capture
        self.is_run = False

        self.calFunc = {}
        self.calFunc["sharpness"] = self.get_sharpness
        self.calFunc["chroma stdev"] = self.get_chroma_stdev
        self.calFunc["luma stdev"] = self.get_luma_stdev

        # plot
        self.bset_score_plot = MplCanvas_timing(self.ui.label_best_score_plot, color=['r', 'g'], label=['score'])
        self.hyper_param_plot = MplCanvas_timing(self.ui.label_hyper_param_plot, color=['g', 'r'], label=['F', 'Cr'])
        self.loss_plot = MplCanvas_timing(self.ui.label_loss_plot, color=['b'], label=['loss'])
        self.update_plot = MplCanvas_timing(self.ui.label_update_plot, color=['b', 'k'], label=['using ML', 'no ML'])

    def finish_run(self):
        self.is_run = False
        self.ui.btn_run.setText('Run')

    # Tuning
    def run(self):

        # 開啟計時器
        self.start_time_counter()

        Cr_optimiter = HyperOptimizer(init_value=0.3, final_value=0.9, method="exponantial_reverse", rate = 0.05)
        F_optimiter = HyperOptimizer(init_value=0.6, final_value=0.3, method="exponantial", rate=0.2)
        # F_optimiter = HyperOptimizer(init_value=0.7, final_value=0.7, method="constant", rate=0.2)

        bounds = self.setting.params['bounds']
        popsize = self.setting.params['population size']
        generations = self.setting.params['generations']
        dimensions = self.setting.params['dimensions']
        capture_num = self.setting.params['capture num']

    
        # 所有參數值
        param_value = np.array(self.setting.params['param_value'])
        # 需要tune的參數位置
        param_change_idx = self.setting.params['param_change_idx']
        # 需要tune的參數個數
        param_change_num = len(param_change_idx)

        trigger_idx = self.setting.params["trigger_idx"]
        print('trigger_idx:', trigger_idx)

        # target score
        type_IQM = np.array(self.setting.params["target_type"])
        target_IQM = np.array(self.setting.params["target_score"])
        weight_IQM = np.array(self.setting.params["target_weight"])
        print(type_IQM, target_IQM, weight_IQM)

        self.setup_param_window_signal.emit(popsize, param_change_num, type_IQM)

        self.reset()

        # 取得每個參數的邊界
        min_b, max_b = np.asarray(bounds).T
        min_b = min_b[param_change_idx]
        max_b = max_b[param_change_idx]

        # 初始化20群(population) normalize: [0, 1]
        pop = np.random.rand(popsize, param_change_num)
        pop = np.around(pop, 8)
        self.setting.params['pop'] = []

        # denormalize to [min_b, max_b]
        diff = np.fabs(min_b - max_b)
        pop_denorm = min_b + pop * diff

        best_score = 1e9
        # Measure Initial Score
        self.mkdir('best')
        self.ui.label_generation.setText("initialize")
        fitness = np.zeros(popsize)  # 計算popsize個individual所產生的影像的分數
        IQMs = []

        ##### ML #####
        input_dim = dimensions
        output_dim = len(target_IQM)
        self.ML = ML(self.setting.params['pretrain_model'], self.setting.params['train'], input_dim, output_dim)
        ##### ML #####

        # initial individual
        for idx in range(popsize):
            print('\n\ninitial individual:', idx)
            param_value[param_change_idx] = pop_denorm[idx]
            now_IQM = self.measure_score_by_param_value(type_IQM, param_value, 'best/'+str(idx), idx, trigger_idx, capture_num)
            fitness[idx] = self.cal_score_by_weight(now_IQM, target_IQM, weight_IQM, np.ones(target_IQM.shape))
            IQMs.append(now_IQM)
            self.setting.params['pop'].append(pop[idx])
            self.update_param_window_signal.emit(idx, pop_denorm[idx], fitness[idx], now_IQM)
            print('now IQM', now_IQM)
            print('now score', fitness[idx])

            if fitness[idx] < best_score:
                best_score = fitness[idx]
                # 將目前最佳值更新在UI上
                self.ui.statusbar.showMessage('individual {} get the better score'.format(idx), 5000)
                self.ui.label_score.setText(str(np.round(best_score, 9)))

                # 將最佳分數更新在UI上
                idx = 0
                for P in self.ui.ParamModifyBlock:
                    for E in P.lineEdits:
                        E.setText(str(param_value[idx]))
                        idx += 1
                print('now best_idx', idx)

        # find the best pop(score最小的pop)
        best_idx = np.argmin(fitness)
        print('best_idx', best_idx)
        assert best_score == fitness[best_idx]
        IQMs = np.array(IQMs)
        # 暫時開啟std_IQM
        std_IQM = IQMs.std(axis=0)
        print(std_IQM)

        update_rate = 0
        ML_update_rate = 0
        # Do Differential Evolution
        for i in range(generations):
            update_times = 0
            ML_update_times = 0

            self.ui.label_generation.setText(str(i))
            F = F_optimiter.update(i)
            Cr = Cr_optimiter.update(i)

            # 創資料夾
            gen_dir = 'generation{}'.format(i)
            self.mkdir(gen_dir)

            for j in range(popsize):
                self.ui.label_individual.setText(str(j))
                # select all pop except j
                idxs = [idx for idx in range(popsize) if idx != j]
                # random select three pop except j
                a, b, c = pop[np.random.choice(idxs, 3, replace=False)]

                # Mutation
                mutant = np.clip(a + F * (b - c), 0, 1)

                # random choose the dimensions
                cross_points = np.random.rand(param_change_num) < Cr
                # if no dimensions be selected
                if not np.any(cross_points):
                    # random choose one dimensions
                    cross_points[np.random.randint(0, param_change_num)] = True

                # 隨機替換突變
                trial = np.where(cross_points, mutant, pop[j])
                trial = np.around(trial, 8)

                # denormalize
                trial_denorm = min_b + trial * diff
                param_value[param_change_idx] = trial_denorm

                # mesure score
                print('\n\ngenerations:', i, 'individual:', j)
                now_IQM = self.measure_score_by_param_value(type_IQM, param_value, '{}/{}'.format(gen_dir, j), j, trigger_idx, capture_num)
                f = self.cal_score_by_weight(now_IQM, target_IQM, weight_IQM, std_IQM)
                print('now IQM', now_IQM)
                print('now fitness', f)
                if f < fitness[j]: update_times += 1

                # # use model to predict
                # if (self.ML.PRETRAIN_MODEL or self.ML.TRAIN) and i>=self.ML.pred_idx:
                #     self.ML.model.eval()
                #     diff_target_IQM = target_IQM - IQMs[j]
                #     times = 0
                #     x = np.zeros(dimensions)
                #     x[param_change_idx] = trial - pop[j]
                #     pred_dif_IQM = self.ML.model(torch.FloatTensor(x.tolist())).detach().numpy()
                    
                #     while (pred_dif_IQM * weight_IQM * diff_target_IQM <= 0).all() and times<50: # 如果預測分數會上升就重找參數
                #         times+=1
                #         # select all pop except j
                #         idxs = [idx for idx in range(popsize) if idx != j]
                #         # random select two pop except j
                #         a, b, c = pop[np.random.choice(idxs, 3, replace=False)]

                #         # Mutation
                #         mutant = np.clip(a + F*(b - c), 0, 1)

                #         # random choose the dimensions
                #         cross_points = np.random.rand(param_change_num) < Cr
                #         # if no dimensions be selected
                #         if not np.any(cross_points):
                #             # random choose one dimensions
                #             cross_points[np.random.randint(0, param_change_num)] = True

                #         # 隨機替換突變
                #         trial = np.where(cross_points, mutant, pop[j])
                #         trial = np.round(trial, 8)

                #         x = np.zeros(dimensions)
                #         x[param_change_idx] = trial - pop[j]
                #         pred_dif_IQM = self.ML.model(torch.FloatTensor(x.tolist())).detach().numpy()

                #     print(times)

                # # denormalize
                # trial_denorm = min_b + trial * diff

                # # add fix value
                # param_value[param_change_idx] = trial_denorm

                # ##### ML #####
                # if self.ML.TRAIN:
                #     print('ML train')
                #     # 建立一個子執行緒
                #     self.train_task = threading.Thread(target = lambda: self.ML.train(i, self.loss_plot))
                #     # 當主程序退出，該執行緒也會跟著結束
                #     self.train_task.daemon = True
                #     # 執行該子執行緒
                #     self.train_task.start()
                # ##### ML #####

                # # mesure score
                # print('\n\ngenerations:', i, 'individual:', j)
                # now_IQM = self.measure_score_by_param_value(type_IQM, param_value, '{}/{}'.format(gen_dir, j), j, trigger_idx, capture_num)
                # f = self.cal_score_by_weight(now_IQM, target_IQM, weight_IQM, std_IQM)
                # print('now IQM', now_IQM)
                # print('now fitness', f)

                # if self.ML.TRAIN and i>0:
                #     self.train_task.join()

                # ##### ML #####
                # if self.ML.PRETRAIN_MODEL or self.ML.TRAIN:
                #     x = np.zeros(dimensions)
                #     x[param_change_idx] = trial - pop[j]
                #     y = now_IQM - IQMs[j]

                #     self.ML.x_train.append(x.tolist())
                #     self.ML.y_train.append(y.tolist())
                # ##### ML #####

                # 如果突變種比原本的更好
                if f < fitness[j]:
                    # if self.ML.PRETRAIN_MODEL or self.ML.TRAIN: ML_update_times += 1
                    # 替換原本的個體
                    print('replace with better score', f)
                    self.ui.statusbar.showMessage('generation {} individual {} replace with better score'.format(i, j), 5000)
                    fitness[j] = f
                    IQMs[j] = now_IQM
                    pop[j] = trial
                    self.setting.params['pop'][j] = trial.tolist()

                    # update_param_window
                    self.update_param_window_signal.emit(j, trial_denorm, f, now_IQM)

                    # 如果突變種比最優種更好
                    if f < best_score:
                        self.update_param_window_signal.emit(j, trial_denorm, f, now_IQM)

                        # 替換最優種
                        print('replace with best score', f)
                        self.ui.statusbar.showMessage('generation {} individual {} get best score'.format(i, j), 5000)
                        best_idx = j
                        best_score = fitness[best_idx]

                        # 搬移到best資料夾
                        for i in range(capture_num):
                            if capture_num==1:
                                p = '{}.jpg'.format(j)
                            else:
                                p='{}_{}.jpg'.format(j, i)

                            src='{}/{}'.format(gen_dir, p)
                            des='best/{}'.format(p)

                            if os.path.exists(des): os.remove(des)
                            os.replace(src,des)

                        # 將目前最佳值更新在UI上
                        self.ui.label_score.setText(str(np.round(best_score, 9)))

                        # 將最佳參數更新在UI上
                        idx = 0
                        for P in self.ui.ParamModifyBlock:
                            for E in P.lineEdits:
                                E.setText(str(param_value[idx]))
                                E.setCursorPosition(0)
                                idx += 1
                    self.ui.label_score.setText(str(np.round(fitness[best_idx], 5)))
                    if f < 1e-6: self.is_run = False

                self.bset_score_plot.update([fitness[best_idx]])
                self.hyper_param_plot.update([F, Cr])
                self.update_plot.update([ML_update_rate, update_rate])

                if not self.is_run:
                    self.finish_run()
                    sys.exit()

            update_rate = update_times/popsize
            ML_update_rate = ML_update_times/popsize

        self.finish_run()

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print("The", path, "dir is created!")

    def measure_score_by_param_value(self, type_IQM, param_value, path, idx, trigger_idx, capture_num):

        roi = self.setting.params['roi']
        param_names = self.setting.params['param_names']
        xml_path = self.setting.params['xml_path']
        
        if not os.path.exists(xml_path):
            print("The", xml_path, "doesn't exists")
            self.finish_run()
            sys.exit()

        # print('param_value =', param_value)
        self.setParamToXML(param_names, xml_path, param_value, trigger_idx)

        # 使用bat編譯，將bin code推入手機
        self.buildAndPushToCamera()
        sleep(6)

        # 拍照
        self.capture.capture(path, capture_num=capture_num)

        # 計算分數
        now_IQM = self.measure_score_by_multiple_capture(type_IQM, path, roi, capture_num)
        self.ui.label_individual.setText(str(idx))

        return now_IQM

    def setParamToXML(self, param_names, xml_path, params, trigger_idx):
        # 從檔案載入並解析 XML 資料
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_wnr24_aec_datas  =  root.findall("chromatix_wnr24_core/mod_wnr24_post_scale_ratio_data/"\
                            "post_scale_ratio_data/mod_wnr24_pre_scale_ratio_data/"\
                            "pre_scale_ratio_data/mod_wnr24_total_scale_ratio_data/"\
                            "total_scale_ratio_data/mod_wnr24_drc_gain_data/"\
                            "drc_gain_data/mod_wnr24_hdr_aec_data/hdr_aec_data/"\
                            "mod_wnr24_aec_data"
                            )

        for i, ele in enumerate(mod_wnr24_aec_datas):
            if i==trigger_idx:
                wnr24_rgn_data = ele.find("wnr24_rgn_data")
                dim = 0
                for param_name in param_names:
                    parent = wnr24_rgn_data.find(param_name+'_tab')
                    length = int(parent.attrib['length'])

                    param_value_new = params[dim: dim+length]
                    param_value_new = [str(x) for x in param_value_new]
                    param_value_new = ' '.join(param_value_new)

                    # print('old param', wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)
                    wnr24_rgn_data.find(param_name+'_tab/' + param_name).text = param_value_new
                    # print('new param',wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)

                    dim += length
                break

        # write the xml file
        tree.write(xml_path, encoding='UTF-8', xml_declaration=True)


    def buildAndPushToCamera(self):
        print('push bin to camera...')
        call(['adb', 'shell', 'input', 'keyevent = KEYCODE_HOME'])
        v1 = self.setting.params["exe_path"]
        v2 = self.setting.params["project_path"]
        v3 = self.setting.params["bin_name"]
        os.system("build_and_push.bat {} {} {}".format(v1, v2, v3))
        self.capture.clear_camera_folder()

    def measure_score_by_multiple_capture(self, type_IQM, path, roi, capture_num):
        IQM_scores = []
        # print("\n---------IQM score--------\n")
        for i in range(capture_num):
            # 讀取image檔案
            if capture_num==1: p = str(path+".jpg")
            else: p = path+"_"+str(i)+".jpg"
            img = cv2.imread(p, cv2.IMREAD_COLOR)
            IQM_scores.append(self.calIQM(type_IQM, img, roi))
            # print(i, IQM_scores[i])

        IQM_scores = np.array(IQM_scores)
        zscore = stats.zscore(IQM_scores)
        # print("\n---------zscore--------\n")
        # for i in range(capture_num):
        # print(i, zscore[i])
        select = (np.abs(zscore) < 1).all(axis=1)
        # print(select)

        # print("\n---------after drop outlier => [abs(zscore) > 1]--------\n")
        if (select == True).any():
            IQM_scores = IQM_scores[select]
        # print(IQM_scores)

        # 計算分數
        now_IQM = np.mean(IQM_scores, axis=0)
        return now_IQM

    def get_sharpness(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return np.sqrt(cv2.Laplacian(img, cv2.CV_64F).var())

    def get_chroma_stdev(self, img):
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(img_yuv)
        return u.std()+v.std()

    # Reference: J. Immerkær, “Fast Noise Variance Estimation”, Computer Vision and Image Understanding, Vol. 64, No. 2, pp. 300-302, Sep. 1996 [PDF]
    def get_luma_stdev(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        H, W = img.shape

        M = [[1, -2, 1],
             [-2, 4, -2],
             [1, -2, 1]]

        sigma = np.sum(np.sum(np.absolute(convolve2d(img, M))))
        sigma = sigma * math.sqrt(0.5 * math.pi) / (6 * (W-2) * (H-2))

        return sigma

    def calIQM(self, type_IQM, img, rois):
        now_IQM=[]
        for i, roi in enumerate(rois):
            if len(roi)==0: continue
            x, y, w, h = roi
            roi_img = img[y: y+h, x:x+w]
            now_IQM.append(self.calFunc[type_IQM[i]](roi_img))
        
        now_IQM = np.array(now_IQM)
        return now_IQM

    def cal_score_by_weight(self, now_IQM, target_IQM, weight_IQM, std_IQM):
        # 暫時將 std_IQM 開啟
        return (np.abs(target_IQM-now_IQM)/std_IQM).dot(weight_IQM.T)

    def reset(self):
        # reset plot
        self.bset_score_plot.reset()
        self.hyper_param_plot.reset()
        self.loss_plot.reset()
        self.update_plot.reset()

        self.ui.label_generation.setText("#")
        self.ui.label_individual.setText("#")
        self.ui.label_score.setText("#")

    def set_time_counter(self):
        time_counter = 0
        while self.is_run:
            total_sec = time_counter
            hour = max(0, total_sec//3600)
            minute = max(0, total_sec//60 - hour * 60)
            sec = max(0, (total_sec - (hour * 3600) - (minute * 60)))
            # show time_counter (by format)
            self.ui.label_time.setText(str(f"{hour}:{minute:0>2}:{sec:0>2}"))

            sleep(1)
            time_counter += 1

    def start_time_counter(self):
        # 建立一個子執行緒
        self.timer = threading.Thread(target=self.set_time_counter)
        # 當主程序退出，該執行緒也會跟著結束
        self.timer.daemon = True
        # 執行該子執行緒
        self.timer.start()

    def put_param_to_phone(self, idx):
        QMessageBox.about(self, "info", "功能未完善")
        return

        if idx>=len(self.setting.params['pop']):
            QMessageBox.about(self, "info", "目前無參數可推")
            return

        if self.is_run:
            QMessageBox.about(self, "info", "程式還在執行中\n請按stop停止\n或等執行完後再推")
            return
        
        param_names = self.setting.params['param_names']
        xml_path = self.setting.params['xml_path']
        # 所有參數值
        param_value = np.array(self.setting.params['param_value'])
        # 需要tune的參數位置
        param_change_idx = self.setting.params['param_change_idx']
        # 取得每個參數的邊界
        bounds = self.setting.params['bounds']
        min_b, max_b = np.asarray(bounds).T
        min_b = min_b[param_change_idx]
        max_b = max_b[param_change_idx]
        # 取得參數
        trial = self.setting.params['pop'][idx]
        # denormalize to [min_b, max_b]
        diff = np.fabs(min_b - max_b)
        trial_denorm = min_b + trial * diff
        param_value[param_change_idx] = trial_denorm
        self.setParamToXML(param_names, xml_path, param_value)
        # 使用bat編譯，將bin code推入手機
        self.buildAndPushToCamera()

        print('push individual', idx, 'to phone')
        print('param_value =', param_value)
        print("成功推入手機")

        
