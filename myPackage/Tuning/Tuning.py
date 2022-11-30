from PyQt5.QtWidgets import QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, QObject, Qt

from .HyperOptimizer import HyperOptimizer
from .MplCanvasTiming import MplCanvasTiming
from .ImageMeasurement import *
from myPackage.ML.ML import ML

import numpy as np
from time import sleep
from subprocess import call
import xml.etree.ElementTree as ET
from scipy import stats  # zcore
import os
import sys
import cv2
import math
import threading
import shutil
import json

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
    # logger
    log_info_signal = pyqtSignal(str)
    run_cmd_signal = pyqtSignal(str)
    alert_info_signal = pyqtSignal(str, str)

    def __init__(self, run_page_lower_part, data, config, capture):
        super().__init__()
        self.run_page_lower_part = run_page_lower_part
        self.tab_info = self.run_page_lower_part.tab_info
        self.data = data
        self.config = config
        self.capture = capture
        self.is_run = False
        self.TEST_MODE = False
        self.PRETRAIN = False
        self.TRAIN = False

        self.calFunc = {}
        self.calFunc["sharpness"] = get_sharpness
        self.calFunc["chroma stdev"] = get_chroma_stdev
        self.calFunc["luma stdev"] = get_luma_stdev

        # plot
        self.bset_score_plot = MplCanvasTiming(
            self.run_page_lower_part.tab_score.label_plot, color=['r', 'g'], name=['score'], axis_name=["Generation", "Score"]
        )
        self.hyper_param_plot = MplCanvasTiming(
            self.run_page_lower_part.tab_hyper.label_plot, color=['g', 'r'], name=['F', 'Cr'], axis_name=["Generation", "HyperParam Value"]
        )
        self.loss_plot = MplCanvasTiming(
            self.run_page_lower_part.tab_loss.label_plot, color=['b','g', 'r'], name=['loss'], axis_name=["Epoch/10", "Loss"]
        )
        self.update_plot = MplCanvasTiming(
            self.run_page_lower_part.tab_update.label_plot, color=['b', 'k'], name=['using ML', 'no ML'], axis_name=["Generation", "Update Rate"]
        )

        self.ML = ML(self.loss_plot)


    def show_info_by_key(self, key, data):
        for k in key:
            self.tab_info.show_info("{}: {}".format(k,data[k]))

    def show_info(self):
        # show info
        self.tab_info.label.setAlignment(Qt.AlignLeft)
        self.tab_info.clear()

        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]

        self.tab_info.show_info("\n###### Target ######")
        self.show_info_by_key(["target_type", "target_score", "target_weight"], self.data)

        self.tab_info.show_info("\n###### Tuning Block ######")
        self.show_info_by_key(["page_root", "page_key"], self.data)
        self.show_info_by_key(["trigger_idx", "trigger_name"], self.data)

        self.tab_info.show_info("\n###### Differential evolution ######")
        self.show_info_by_key(["population size","generations","capture num"], self.data)
        self.show_info_by_key(["bounds","dimensions","param_change_idx"], block_data)
        self.tab_info.show_info("{}: {}".format("param_value", self.param_value))

        self.tab_info.show_info("\n###### Mode ######")
        self.show_info_by_key(["TEST_MODE","PRETRAIN","TRAIN"], self.data)

        self.tab_info.show_info("\n###### Project Setting ######")
        self.show_info_by_key(["platform", "project_path", "exe_path", "bin_name"], self.data)

    def run(self):
        self.TEST_MODE = self.data["TEST_MODE"]
        self.PRETRAIN = self.data["PRETRAIN"]
        self.TRAIN = self.data["TRAIN"]

        ##### param setting #####
        self.key = self.data["page_key"]
        config = self.config[self.data["page_root"]][self.data["page_key"]]
        block_data = self.data[self.data["page_root"]][self.data["page_key"]]
        
        # xml path
        self.xml_path = self.data['xml_path']+config["file_path"]
        self.xml_node = config["xml_node"]
        self.data_node = config["data_node"]
        if not os.path.exists(self.xml_path):
            self.log_info_signal.emit("The {} doesn't exists".format(self.xml_path))
            # print("The", self.xml_path, "doesn't exists")
            self.finish_signal.emit()
            sys.exit()

        self.exe_path = self.data["exe_path"]
        self.project_path = self.data["project_path"]
        self.bin_name = self.data["bin_name"]

        # hyperparams
        self.popsize = self.data['population size']
        self.generations = self.data['generations']
        self.capture_num = self.data['capture num']
        # self.Cr_optimiter = HyperOptimizer(init_value=0.3, final_value=0.6, method="exponantial_reverse", rate = 0.03)
        # self.F_optimiter = HyperOptimizer(init_value=1.2, final_value=0.7, method="exponantial", rate=0.5)
        self.F_optimiter = HyperOptimizer(init_value=0.7, final_value=0.7, method="constant")
        self.Cr_optimiter = HyperOptimizer(init_value=0.5, final_value=0.5, method="constant")
        
        # params
        self.param_names = config['param_names']
        self.bounds = block_data['bounds']
        self.dimensions = block_data['dimensions']
        self.param_value = np.array(block_data['param_value']) # 所有參數值
        self.param_change_idx = block_data['param_change_idx'] # 需要tune的參數位置
        self.param_change_num = len(self.param_change_idx) # 需要tune的參數個數
        self.trigger_idx = self.data["trigger_idx"]
        self.trigger_name = self.data["trigger_name"]
        # test mode 下沒改動的地方為0
        if self.TEST_MODE: self.param_value = np.zeros(self.dimensions)

        # target score
        if self.TEST_MODE:
            self.data["target_type"]=["TEST", "TEST2"]
            self.data["target_score"]=[0]*len(self.data["target_type"])
            self.data["target_weight"]=[1]*len(self.data["target_type"])

        self.target_type = np.array(self.data["target_type"])
        self.target_IQM = np.array(self.data["target_score"])
        self.weight_IQM = np.array(self.data["target_weight"])
        self.target_num = len(self.target_type)
        self.std_IQM = np.ones(self.target_num)
        self.loss_plot.setup(self.target_type)

        # target region
        self.roi = self.data['roi']

        # get the bounds of each parameter
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

        # update rate
        self.update_count=0
        self.ML_update_count=0
        self.update_rate=0
        self.ML_update_rate=0

        if len(self.data["target_type"])==0:
            self.alert_info_signal.emit("請先圈ROI", "請先圈ROI")
            self.finish_signal.emit()
            return

        ##### start tuning #####
        # setup
        self.show_info()
        self.setup()
        self.initial_individual()

        # ML
        self.ML.reset(
            TEST_MODE = self.TEST_MODE,
            PRETRAIN=self.PRETRAIN, 
            TRAIN=self.TRAIN, 
            
            target_type = self.target_type,
            std_IQM = self.std_IQM,
            key = self.data["page_key"],
            
            input_dim=self.dimensions, 
            output_dim=len(self.target_type)
        )

        # Do Differential Evolution
        for gen_idx in range(self.generations):
            self.run_DE_for_a_generation(gen_idx)
        
        self.finish_signal.emit()


    def initial_individual(self):
        # 刪除資料夾
        if os.path.exists('best'): shutil.rmtree('best')
        self.mkdir('best')
        self.set_generation_signal.emit("initialize")

        # initial individual
        for ind_idx in range(self.popsize):
            self.mkdir('best/'+str(ind_idx))
            self.set_individual_signal.emit(str(ind_idx))
            self.log_info_signal.emit('\ninitial individual: {}'.format(ind_idx))

            # denormalize to [min_b, max_b]
            trial_denorm = self.min_b + self.pop[ind_idx] * self.diff
            # update param_value
            self.param_value[self.param_change_idx] = trial_denorm
            # trial_denorm = np.around(trial_denorm, 4)

            # measure score
            now_IQM = self.measure_score_by_param_value('best/'+str(ind_idx)+'/init_'+str(ind_idx), self.param_value, train=False)
            self.fitness.append(np.around(self.cal_score_by_weight(now_IQM), 9))
            self.IQMs.append(now_IQM)
            self.log_info_signal.emit('now IQM {}'.format(now_IQM))
            self.log_info_signal.emit('now score {}'.format(self.fitness[ind_idx]))

            # update_param_window
            self.update_param_window_signal.emit(ind_idx, trial_denorm, self.fitness[ind_idx], now_IQM)

            if self.fitness[ind_idx] < self.best_score:
                self.update_best_score(ind_idx, self.fitness[ind_idx])

            # 儲存xml
            des="best/init{}.xml".format(ind_idx)
            shutil.copyfile(self.xml_path, des)

        # # 複製整個資料夾
        # if os.path.exists("best_initial"): shutil.rmtree("best_initial")
        # shutil.copytree("best", "best_initial")
        # # 刪除xml
        # for f in os.listdir("best"):
        #     if ".xml" in f:
        #         os.remove("best/"+f)

        self.IQMs = np.array(self.IQMs)
        self.std_IQM = self.IQMs.std(axis=0)
        # 暫時將std設為1
        self.std_IQM = self.std_IQM = np.ones(self.target_num)
        print('std_IQM',self.std_IQM)

    def run_DE_for_a_generation(self, gen_idx):
        self.set_generation_signal.emit(str(gen_idx))

        # create dir
        gen_dir = 'generation{}'.format(gen_idx)
        self.mkdir(gen_dir)

        # update hyperparam
        F = self.F_optimiter.update(gen_idx)
        Cr = self.Cr_optimiter.update(gen_idx)

        self.update_count=0
        self.ML_update_count=0

        for ind_idx in range(self.popsize):
            self.run_DE_for_a_individual(F, Cr, gen_idx, ind_idx, gen_dir)

        # # 複製整個資料夾
        # if os.path.exists("best_gen{}".format(gen_idx)): shutil.rmtree("best_gen{}".format(gen_idx))
        # shutil.copytree("best", "best_gen{}".format(gen_idx)) 
        # remove gen_dir
        shutil.rmtree(gen_dir)
        # # 刪除xml
        # for f in os.listdir("best"):
        #     if ".xml" in f:
        #         os.remove("best/"+f)
        
        self.update_rate=self.update_count/self.popsize
        self.ML_update_rate=self.ML_update_count/self.popsize
        

    def run_DE_for_a_individual(self, F, Cr, gen_idx, ind_idx, gen_dir):
        self.set_individual_signal.emit(str(ind_idx))

        trial, trial_denorm = self.generate_parameters(ind_idx, F, Cr)
        # update param_value
        self.param_value[self.param_change_idx] = trial_denorm

        if self.TEST_MODE:
            # mesure score
            # self.log_info_signal.emit("generations:{}, individual:{}".format(gen_idx, ind_idx))
            now_IQM = self.measure_score_by_param_value('{}/{}'.format(gen_dir, ind_idx), self.param_value, train=False)
            f = np.around(self.cal_score_by_weight(now_IQM), 9)
            # self.log_info_signal.emit("now IQM {}".format(now_IQM))
            # self.log_info_signal.emit("now fitness {}".format(f))
            if (self.PRETRAIN or self.TRAIN) and f < self.fitness[ind_idx]: self.update_count+=1

        # use model to predict
        if (self.PRETRAIN or self.TRAIN) and gen_idx>=self.ML.pred_idx:
            trial, trial_denorm = self.get_best_trial(ind_idx, F, Cr, trial, trial_denorm)
            # times = 0
            # while self.is_bad(trial, ind_idx, times) and times<50:
            #     trial, trial_denorm = self.generate_parameters(ind_idx, F, Cr)
            #     times+=1
            # self.log_info_signal.emit("times: {}".format(times))                
            
        # update param_value
        self.param_value[self.param_change_idx] = trial_denorm

        # mesure score
        # self.log_info_signal.emit("generations:{}, individual:{}".format(gen_idx, ind_idx))
        now_IQM = self.measure_score_by_param_value('{}/gne{}_ind{}'.format(gen_dir, gen_idx, ind_idx), self.param_value, train=gen_idx>=self.ML.train_idx)
        f = np.around(self.cal_score_by_weight(now_IQM), 9)
        self.log_info_signal.emit("now IQM {}".format(now_IQM))
        self.log_info_signal.emit("now fitness {}".format(f))

        # update dataset
        if (self.PRETRAIN or self.TRAIN):
            x = np.zeros(self.dimensions)
            x[self.param_change_idx] = trial - self.pop[ind_idx]
            y = now_IQM - self.IQMs[ind_idx]
            self.ML.update_dataset(x, y)

        # 如果突變種比原本的更好
        if f < self.fitness[ind_idx]:
            # update_param_window
            self.update_param_window_signal.emit(ind_idx, trial_denorm, f, now_IQM)
            
            if (self.PRETRAIN or self.TRAIN): self.ML_update_count+=1
            else: self.update_count+=1

            # 替換原本的個體
            self.log_info_signal.emit('replace with better score {}'.format(f))
            self.set_statusbar_signal.emit('generation {} individual {} replace with better score'.format(gen_dir, ind_idx))
            
            self.fitness[ind_idx] = f
            self.IQMs[ind_idx] = now_IQM
            self.pop[ind_idx] = trial

            # 將圖片搬移到best資料夾
            if not self.TEST_MODE:
                for i in range(self.capture_num):
                    if self.capture_num==1:
                        src_img = 'gne{}_ind{}.jpg'.format(gen_idx ,ind_idx)
                        des_img = '{}.jpg'.format(f) # 根據量化分數命名
                        
                    else:
                        src_img = 'gne{}_ind{}_{}.jpg'.format(gen_idx, ind_idx, i)
                        des_img = '{}_{}.jpg'.format(f, i) # 根據量化分數命名

                    src='{}/{}'.format(gen_dir, src_img)
                    des='best/{}'.format(des_img) # 根據量化分數命名

                    if os.path.exists(des): os.remove(des)
                    os.replace(src,des)
            # 儲存json
            info = {
                "name": 'gne{}_ind{}'.format(gen_idx ,ind_idx),
                "param_block": self.key,
                "trigger_block": self.trigger_name,
                "param_name": self.param_names,
                "param_value": self.param_value,
                "target_type": self.target_type,
                "target_IQM": self.target_IQM,
                "now_IQM": now_IQM,
                "score": f
            }
            with open('gne{}_ind{}.json'.format(gen_idx ,ind_idx), "w") as outfile:
                outfile.write(json.dumps(info, indent=4))

            # 儲存xml
            des="best/gen{}_ind{}.xml".format(gen_idx, ind_idx)
            shutil.copyfile(self.xml_path, des)

            # 如果突變種比最優種更好
            if f < self.best_score:
                # 替換最優種
                self.update_best_score(ind_idx, f)
                    
                if f==0:
                    self.finish_signal.emit()
                    sys.exit()

        self.bset_score_plot.update([self.best_score])
        self.hyper_param_plot.update([F, Cr])
        self.update_plot.update([self.ML_update_rate, self.update_rate])

    def start_ML_train(self):
        # print('ML train')
        # 建立一個子執行緒
        self.train_task = threading.Thread(target = lambda: self.ML.train())
        # 當主程序退出，該執行緒也會跟著結束
        self.train_task.daemon = True
        # 執行該子執行緒
        self.train_task.start()

    def get_best_trial(self, ind_idx, F, Cr, trial, trial_denorm):
        best_trial, best_trial_denorm = trial, trial_denorm
        best_good_num = 0
        times = 0
        for i in range(20):
            x = np.zeros(self.dimensions)
            x[self.param_change_idx] = trial - self.pop[ind_idx] # 參數差
            diff_target_IQM = self.target_IQM - self.IQMs[ind_idx] # 目標差
            pred_dif_IQM = self.ML.predict(x)

            good_num = np.sum(pred_dif_IQM * self.weight_IQM * diff_target_IQM > 0)
            if good_num > best_good_num:
                best_trial, best_trial_denorm = trial, trial_denorm
                times = i
                if good_num==self.target_num:
                    break

            trial, trial_denorm = self.generate_parameters(ind_idx, F, Cr)

        self.log_info_signal.emit("times: {}".format(times))  
        return best_trial, best_trial_denorm

    def is_bad(self, trial, ind_idx, times):
        x = np.zeros(self.dimensions)
        x[self.param_change_idx] = trial - self.pop[ind_idx] # 參數差
        diff_target_IQM = self.target_IQM - self.IQMs[ind_idx] # 目標差
        pred_dif_IQM = self.ML.predict(x)
        ##### 更改判斷標準(bad大於半數) #####
        bad_num = np.sum(pred_dif_IQM * self.weight_IQM * diff_target_IQM <= 0)
        if times<10:
            return bad_num >= 1
        else: 
            return bad_num >= np.ceil(self.target_num/2)


    def generate_parameters(self, ind_idx, F, Cr):
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
        # trial_denorm = np.around(trial_denorm, 4)

        return trial, trial_denorm


    def update_best_score(self, idx, score):
        # update best score
        self.best_score = np.round(score, 9)
        # print('replace with best score')
        # print('now best_idx', idx, 'now best_score', score)
        # update best score to UI
        # self.ui.statusbar.showMessage('individual {} get the better score'.format(idx), 3000)
        self.set_score_signal.emit(str(self.best_score))
        # update best param to UI
        # self.update_param_window_signal.emit(idx, pop_denorm[idx], fitness[idx], now_IQM)
        

    def measure_score_by_param_value(self, path, param_value, train):
        
        # print('param_value =', param_value)
        if self.TEST_MODE: 
            if self.TRAIN and train:
                self.start_ML_train()
                self.train_task.join()
            return np.array([self.fobj(param_value)]*len(self.target_type))

        # write param_value to xml
        self.setParamToXML(param_value)

        # compile project using bat. push bin code to camera
        self.buildAndPushToCamera(self.exe_path, self.project_path, self.bin_name)
        if self.TRAIN and train: self.start_ML_train()
        sleep(12)

        # 拍照
        self.capture.capture(path, capture_num=self.capture_num)

        # 計算分數
        now_IQM = self.measure_score_by_multiple_capture(path)

        # 等ML train完再繼續
        if self.TRAIN and train: self.train_task.join()
        
        return now_IQM

    def setParamToXML(self, param_value):
        # 從檔案載入並解析 XML 資料
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # 子節點與屬性
        mod_aec_datas = root.findall(self.xml_node)

        if self.key == "ASF":
            param_value = np.concatenate([[p]*64 for p in param_value])

        if self.key == "ABF":
            param_value = np.concatenate([[p]*n for p,n in zip(param_value, [2,2,1])])
            print('setParamToXML', param_value)

        for i, ele in enumerate(mod_aec_datas):
            if i==self.trigger_idx:
                rgn_data = ele.find(self.data_node)
                dim = 0
                for param_name in self.param_names:
                    parent = rgn_data.find(param_name+'_tab')
                    if parent:

                        length = int(parent.attrib['length'])

                        param_value_new = param_value[dim: dim+length]
                        param_value_new = [str(x) for x in param_value_new]
                        param_value_new = ' '.join(param_value_new)

                        # print('old param', wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)
                        rgn_data.find(param_name+'_tab/' + param_name).text = param_value_new
                        # print('new param',wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)

                    else:
                        parent = rgn_data.find(param_name)

                        length = int(parent.attrib['length'])

                        param_value_new = param_value[dim: dim+length]
                        param_value_new = [str(x) for x in param_value_new]
                        param_value_new = ' '.join(param_value_new)

                        # print('old param', wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)
                        parent.text = param_value_new
                        # print('new param',wnr24_rgn_data.find(param_name+'_tab/'+param_name).text)


                    dim += length
                break

        # write the xml file
        tree.write(self.xml_path, encoding='UTF-8', xml_declaration=True)

    def buildAndPushToCamera(self, exe_path, project_path, bin_name):
        self.log_info_signal.emit('push bin to camera...')
        self.run_cmd_signal.emit('adb shell input keyevent = KEYCODE_HOME')
        self.run_cmd_signal.emit("build_and_push.bat {} {} {}".format(exe_path, project_path, bin_name))
        self.capture.clear_camera_folder()
        self.log_info_signal.emit('wait for reboot camera...')

    def measure_score_by_multiple_capture(self, path):
        IQM_scores = []
        # print("\n---------IQM score--------\n")
        for i in range(self.capture_num):
            # 讀取image檔案
            if self.capture_num==1: p = str(path+".jpg")
            else: p = path+"_"+str(i)+".jpg"
            img = cv2.imread(p, cv2.IMREAD_COLOR)
            IQM_scores.append(self.calIQM(img))
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
            now_IQM.append(self.calFunc[self.target_type[i]](roi_img))
        
        now_IQM = np.array(now_IQM)
        return now_IQM

    def cal_score_by_weight(self, now_IQM):
        if self.TEST_MODE: return np.mean(now_IQM)
        return (np.abs(self.target_IQM-now_IQM)/self.std_IQM).dot(self.weight_IQM.T)

    def mkdir(self, path):
        if self.TEST_MODE: 
            print('mkdir {} return because TEST_MODE'.format(path))
            return
        if not os.path.exists(path):
            os.makedirs(path)
            print("The", path, "dir is created!")

    def setup(self):
        # reset plot
        self.bset_score_plot.reset()
        self.hyper_param_plot.reset()
        self.loss_plot.reset()
        self.update_plot.reset()

        # reset label
        self.set_score_signal.emit("#")
        self.set_generation_signal.emit("#")
        self.set_individual_signal.emit("#")

        self.setup_param_window_signal.emit(self.popsize, self.param_change_num, self.target_type)

    # def push_to_phone(self, idx):
    #     if self.TEST_MODE:
    #         QMessageBox.about(self, "info", "TEST_MODE下不可推")
    #         print("TEST_MODE下不可推")
    #     # QMessageBox.about(self, "info", "功能未完善")
    #     # return

    #     if idx>=len(self.fitness):
    #         QMessageBox.about(self, "info", "目前無參數可推")
    #         return

    #     if self.is_run:
    #         QMessageBox.about(self, "info", "程式還在執行中\n請按stop停止\n或等執行完後再推")
    #         return
        
    #     # get normalized parameters
    #     trial = self.pop[idx]
    #     # denormalize to [min_b, max_b]
    #     trial_denorm = self.min_b + trial * self.diff
    #     # update param_value
    #     self.param_value[self.param_change_idx] = trial_denorm

    #     self.setParamToXML(self.param_value)
    #     # 使用bat編譯，將bin code推入手機
    #     self.buildAndPushToCamera()

    #     print('push individual', idx, 'to phone')
    #     print('param_value =', self.param_value)
    #     print("成功推入手機")

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

