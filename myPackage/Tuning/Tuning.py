from PyQt5.QtWidgets import QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, QObject

from .HyperOptimizer import HyperOptimizer
from .MplCanvasTiming import MplCanvasTiming

import numpy as np
from time import sleep
from subprocess import call
import xml.etree.ElementTree as ET
from scipy import stats  # zcore
import os
import sys
import cv2
import math

class Tuning(QObject):  # 要繼承QWidget才能用pyqtSignal!!
    finish_signal = pyqtSignal()
    # UI
    set_score_signal = pyqtSignal(str)
    set_generation_signal = pyqtSignal(str)
    set_individual_signal = pyqtSignal(str)
    set_statusbar_signal = pyqtSignal(str)
    # param window
    show_param_window_signal = pyqtSignal()
    setup_param_window_signal = pyqtSignal(int, int, np.ndarray) # popsize, param_change_num, IQM_names
    update_param_window_signal = pyqtSignal(int, np.ndarray, float, np.ndarray)

    def __init__(self, ui, data, config, capture):
        super().__init__()
        self.ui = ui
        self.data = data
        self.config = config
        self.capture = capture
        self.is_run = False
        self.TEST_MODE = True

        # plot
        self.bset_score_plot = MplCanvasTiming(self.ui.tab3.lower_part.tab_score.label_plot, color=['r', 'g'], label=['score'])
        self.hyper_param_plot = MplCanvasTiming(self.ui.tab3.lower_part.tab_hyper.label_plot, color=['g', 'r'], label=['F', 'Cr'])

    def run(self):
        ##### param setting #####
        print('self.TEST_MODE =',self.TEST_MODE)
        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        
        # xml path
        self.xml_path = self.data['xml_path']+config["file_path"]
        self.xml_node = config["xml_node"]
        if not os.path.exists(self.xml_path):
            print("The", self.xml_path, "doesn't exists")
            self.finish_signal.emit()
            sys.exit()


        # hyperparams
        self.popsize = self.data['population size']
        self.generations = self.data['generations']
        self.capture_num = self.data['capture num']
        self.Cr_optimiter = HyperOptimizer(init_value=0.3, final_value=0.5, method="exponantial_reverse", rate = 0.05)
        # self.F_optimiter = HyperOptimizer(init_value=0.7, final_value=0.5, method="exponantial", rate=0.2)
        self.F_optimiter = HyperOptimizer(init_value=0.7, final_value=0.7, method="constant")
        
        # params
        self.param_names = config['param_names']
        self.bounds = block_data['bounds']
        self.dimensions = block_data['dimensions']
        self.param_value = np.array(block_data['param_value']) # 所有參數值
        self.param_change_idx = block_data['param_change_idx'] # 需要tune的參數位置
        self.param_change_num = len(self.param_change_idx) # 需要tune的參數個數
        self.trigger_idx = block_data["trigger_idx"]
        if self.TEST_MODE: self.param_value = np.zeros(self.dimensions)

        # target score
        self.type_IQM = np.array(self.data["target_type"])
        self.target_IQM = np.array(self.data["target_score"])
        self.weight_IQM = np.array(self.data["target_weight"])
        self.std_IQM=np.ones([len(self.type_IQM)])

        # target region
        self.roi = self.data['roi']

        # get the bounds of each parameter
        print(self.bounds)
        self.min_b, self.max_b = np.asarray(self.bounds).T
        self.min_b = self.min_b[self.param_change_idx]
        self.max_b = self.max_b[self.param_change_idx]
        self.diff = np.fabs(self.min_b - self.max_b)

        # initialize population and normalize to [0, 1]
        self.pop = np.random.rand(self.popsize, self.param_change_num)
        self.pop = np.around(self.pop, 4) # 精度到小數點4位

        # score
        self.best_score = 1e9
        self.fitness = []  # 計算popsize個individual所產生的影像的分數
        self.IQMs = []

        ##### start tuning #####
        # setup
        self.setup()

        self.initial_individual()

        # Do Differential Evolution
        for gen_idx in range(self.generations):
            self.run_DE_for_a_generation(gen_idx)
            
        self.finish_signal.emit()


    def initial_individual(self):
        self.mkdir('best')
        self.set_generation_signal.emit("initialize")

        # initial individual
        for ind_idx in range(self.popsize):
            self.set_individual_signal.emit(str(ind_idx))
            print('\n\ninitial individual:', ind_idx)

            # denormalize to [min_b, max_b]
            trial_denorm = self.min_b + self.pop[ind_idx] * self.diff
            # update param_value
            self.param_value[self.param_change_idx] = trial_denorm

            # measure score
            now_IQM = self.measure_score_by_param_value('best/'+str(ind_idx), self.param_value)
            self.fitness.append(np.around(self.cal_score_by_weight(now_IQM), 9))
            self.IQMs.append(now_IQM)
            print('now IQM', now_IQM)
            print('now score', self.fitness[ind_idx])

            # update_param_window
            self.update_param_window_signal.emit(ind_idx, trial_denorm, self.fitness[ind_idx], now_IQM)

            if self.fitness[ind_idx] < self.best_score:
                self.update_best_score(ind_idx, self.fitness[ind_idx])

        self.IQMs = np.array(self.IQMs)
        std_IQM = self.IQMs.std(axis=0)
        print('std_IQM',std_IQM)

    def run_DE_for_a_generation(self, gen_idx):
        self.set_generation_signal.emit(str(gen_idx))

        # create dir
        gen_dir = 'generation{}'.format(gen_idx)
        self.mkdir(gen_dir)

        # update hyperparam
        F = self.F_optimiter.update(gen_idx)
        Cr = self.Cr_optimiter.update(gen_idx)

        for ind_idx in range(self.popsize):
            self.run_DE_for_a_individual(F, Cr, gen_idx, ind_idx, gen_dir)

    def run_DE_for_a_individual(self, F, Cr, gen_idx, ind_idx, gen_dir):
        self.set_individual_signal.emit(str(ind_idx))

        # select all pop except j
        idxs = [idx for idx in range(self.popsize) if idx != ind_idx]
        # random select three pop except j
        a, b, c = self.pop[np.random.choice(idxs, 3, replace=False)]

        # Mutation
        mutant = np.clip(a + F * (b - c), 0, 1)

        # random choose the dimensions
        cross_points = np.random.rand(self.param_change_num) < Cr
        # if no dimensions be selected
        if not np.any(cross_points):
            # random choose one dimensions
            cross_points[np.random.randint(0, self.param_change_num)] = True

        # random substitution mutation
        trial = np.where(cross_points, mutant, self.pop[ind_idx])
        trial = np.around(trial, 4)

        # denormalize to [min_b, max_b]
        trial_denorm = self.min_b + trial * self.diff
        # update param_value
        self.param_value[self.param_change_idx] = trial_denorm

        # mesure score
        print('\n\ngenerations:', gen_idx, 'individual:', ind_idx)
        now_IQM = self.measure_score_by_param_value('{}/{}'.format(gen_dir, ind_idx), self.param_value)
        f = np.around(self.cal_score_by_weight(now_IQM), 9)
        print('now IQM', now_IQM)
        print('now fitness', f)

        # update_param_window
        self.update_param_window_signal.emit(ind_idx, trial_denorm, f, now_IQM)

        # 如果突變種比原本的更好
        if f < self.fitness[ind_idx]:
            # 替換原本的個體
            print('replace with better score', f)
            self.set_statusbar_signal.emit('generation {} individual {} replace with better score'.format(gen_dir, ind_idx))
            
            self.fitness[ind_idx] = f
            self.IQMs[ind_idx] = now_IQM
            self.pop[ind_idx] = trial

            # 如果突變種比最優種更好
            if f < self.best_score:
                # 替換最優種
                self.update_best_score(ind_idx, f)

                # 搬移到best資料夾
                if not self.TEST_MODE:
                    for i in range(self.capture_num):
                        if self.capture_num==1:
                            p = '{}.jpg'.format(ind_idx)
                        else:
                            p='{}_{}.jpg'.format(ind_idx, i)

                        src='{}/{}'.format(gen_dir, p)
                        des='best/{}'.format(p)

                        if os.path.exists(des): os.remove(des)
                        os.replace(src,des)
                
                if f==0:
                    self.finish_signal.emit()
                    sys.exit()

        self.bset_score_plot.update([self.best_score])
        self.hyper_param_plot.update([F, Cr])


    def update_best_score(self, idx, score):
        # update best score
        self.best_score = np.round(score, 9)
        print('replace with best score')
        print('now best_idx', idx, 'now best_score', score)
        # update best score to UI
        # self.ui.statusbar.showMessage('individual {} get the better score'.format(idx), 3000)
        self.set_score_signal.emit(str(self.best_score))
        # update best param to UI
        # self.update_param_window_signal.emit(idx, pop_denorm[idx], fitness[idx], now_IQM)
        

    def measure_score_by_param_value(self, path, param_value):

        print('param_value =', param_value)
        if self.TEST_MODE: return np.array([self.fobj(param_value)]*len(self.type_IQM))

        # write param_value to xml
        self.setParamToXML(param_value)

        # compile project using bat. push bin code to camera
        self.buildAndPushToCamera()
        sleep(6)

        # 拍照
        self.capture.capture(path, capture_num=self.capture_num)

        # 計算分數
        now_IQM = self.measure_score_by_multiple_capture(path)
        
        return now_IQM

    def setParamToXML(self, param_value):
        # 從檔案載入並解析 XML 資料
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_aec_datas  =  root.findall(self.xml_node)

        for i, ele in enumerate(mod_aec_datas):
            if i==self.trigger_idx:
                wnr24_rgn_data = ele.find("wnr24_rgn_data")
                dim = 0
                for param_name in self.param_names:
                    parent = wnr24_rgn_data.find(param_name+'_tab')
                    length = int(parent.attrib['length'])

                    param_value_new = param_value[dim: dim+length]
                    param_value_new = [str(x) for x in param_value_new]
                    param_value_new = ' '.join(param_value_new)

                    # print('old param', wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)
                    wnr24_rgn_data.find(param_name+'_tab/' + param_name).text = param_value_new
                    # print('new param',wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)

                    dim += length
                break

        # write the xml file
        tree.write(self.xml_path, encoding='UTF-8', xml_declaration=True)

    def buildAndPushToCamera(self):
        print('push bin to camera...')
        call(['adb', 'shell', 'input', 'keyevent = KEYCODE_HOME'])
        v1 = self.data["exe_path"]
        v2 = self.data["project_path"]
        v3 = self.data["bin_name"]
        os.system("build_and_push.bat {} {} {}".format(v1, v2, v3))
        self.capture.clear_camera_folder()

    def measure_score_by_multiple_capture(self, path):
        IQM_scores = []
        # print("\n---------IQM score--------\n")
        for i in range(self.capture_num):
            # 讀取image檔案
            if self.capture_num==1: p = str(path+".jpg")
            else: p = path+"_"+str(i)+".jpg"
            img = cv2.imread(p, cv2.IMREAD_COLOR)
            IQM_scores.append(self.calIQM(self.type_IQM, img, self.roi))
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

    def calIQM(self, img):
        now_IQM=[]
        for i, roi in enumerate(self.roi):
            if len(roi)==0: continue
            x, y, w, h = roi
            roi_img = img[y: y+h, x:x+w]
            now_IQM.append(self.calFunc[self.type_IQM[i]](roi_img))
        
        now_IQM = np.array(now_IQM)
        return now_IQM

    def cal_score_by_weight(self, now_IQM):
        if self.TEST_MODE: return np.mean(now_IQM)
        return (np.abs(self.target_IQM-now_IQM)/self.std_IQM).dot(self.weight_IQM.T)

    def mkdir(self, path):
        if self.TEST_MODE: return
        if not os.path.exists(path):
            os.makedirs(path)
            print("The", path, "dir is created!")

    def setup(self):
        # reset plot
        self.bset_score_plot.reset()
        self.hyper_param_plot.reset()
        # self.loss_plot.reset()
        # self.update_plot.reset()

        # reset label
        self.set_score_signal.emit("#")
        self.set_generation_signal.emit("#")
        self.set_individual_signal.emit("#")

        self.setup_param_window_signal.emit(self.popsize, self.param_change_num, self.type_IQM)

    def push_to_phone(self, idx):
        # QMessageBox.about(self, "info", "功能未完善")
        # return

        if idx>=len(self.fitness):
            QMessageBox.about(self, "info", "目前無參數可推")
            return

        if self.is_run:
            QMessageBox.about(self, "info", "程式還在執行中\n請按stop停止\n或等執行完後再推")
            return
        
        # get normalized parameters
        trial = self.pop[idx]
        # denormalize to [min_b, max_b]
        trial_denorm = self.min_b + trial * self.diff
        # update param_value
        self.param_value[self.param_change_idx] = trial_denorm

        self.setParamToXML(self.param_names, self.xml_path, self.param_value)
        # 使用bat編譯，將bin code推入手機
        self.buildAndPushToCamera()

        print('push individual', idx, 'to phone')
        print('param_value =', self.param_value)
        print("成功推入手機")

    # Ackley
    # objective function
    def fobj(self, X):
        firstSum = 0.0
        secondSum = 0.0
        for c in X:
            firstSum += c**2.0
            secondSum += math.cos(2.0*math.pi*c)
        n = float(len(X))
        return -20.0*math.exp(-0.2*math.sqrt(firstSum/n)) - math.exp(secondSum/n) + 20 + math.e

