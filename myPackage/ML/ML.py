
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

# Pytorch
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import numpy as np
import json
import os

from .model import My_Model

class My_Dataset(Dataset):
    '''
    x: Features.
    y: Targets, if none, do prediction.
    '''

    def __init__(self, x, y):
        self.y = torch.FloatTensor(y)
        self.x = torch.FloatTensor(x)

    def __getitem__(self, idx):
        x = self.x[idx]
        y = self.y[idx]
        return x, y

    def __len__(self):
        return len(self.y)


class ML():
    # logger
    # log_info_signal = pyqtSignal(str)
    # def __init__(self):
    #     super().__init__()
    #     self.epoch_n=100
    #     self.train_idx = 2
    #     self.pred_idx = 3

    #     self.select_threshold = 0.3
    #     self.zero_threshold = 0.05

    #     self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    #     self.target_type = None

    
    # def reset(self, 
    #         TEST_MODE,
    #         key,
    #         target_type, 
    #         std_IQM,  
    #         loss_plot,
    #         PRETRAIN_MODEL=False, 
    #         TRAIN=False, 
    #         input_dim=0, 
    #         output_dim=1
    #     ):

    #     self.TEST_MODE = TEST_MODE
    #     self.key = key
    #     self.target_type = target_type
    #     self.std_IQM = std_IQM
    #     self.loss_plot = loss_plot
    #     self.PRETRAIN_MODEL = PRETRAIN_MODEL
    #     self.TRAIN = TRAIN
    #     self.output_dim = output_dim

    #     self.x_train = []
    #     self.y_train = []
    #     self.models = {}
    #     self.optimizers = {}
    #     self.criterions = {}


    #     for target in self.target_type:
    #         model =  My_Model(input_dim, 1).to(self.device)
    #         self.models[target] = model
    #         self.optimizers[target] = torch.optim.AdamW(self.models[target].parameters(), lr=1e-5)
    #         self.criterions[target] = nn.MSELoss(reduction='mean')


    #     if self.PRETRAIN_MODEL:
    #         self.epoch_n=50
    #         self.pred_idx = 3
    #         for target in self.target_type:
    #             path = "myPackage/ML/Model/{}/{}".format(self.key, target)
    #             if os.path.exists(path):
    #                 self.models[target].load_state_dict(torch.load(path))
    #                 self.optimizers[target] = torch.optim.AdamW(self.models[target].parameters(), lr=1e-7)
    #                 self.log_info_signal.emit("\nLoad pretrain model: {}\n".format(path))
    #             else:
    #                 self.log_info_signal.emit("\n找不到pretrain model: {}\n".format(path))
        



    # def train(self):
        
    #     train_dataset = My_Dataset(self.x_train, self.y_train)
    #     bs = 16
    #     train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=True)

    #     loss_record = []
    #     # for type in self.target_type:
    #     #     loss_record[type] = []
    #     self.models["TEST"].train()

    #     for epoch in range(self.epoch_n):
    #         for x, y in train_loader:
    #             output = self.models["TEST"](x)
    #             loss = self.criterions["TEST"](output, y)
    #             # Compute gradient(backpropagation).
    #             loss.backward()
    #             # Update parameters.
    #             self.optimizers["TEST"].step()
    #             loss_record.append(loss.detach().item())
                
    #         if (epoch+1) % 10 == 0:
    #             mean_train_loss = []
    #             mean_train_loss.append(sum(loss_record)/len(loss_record))
    #             self.loss_plot.update(mean_train_loss)  # plot loss

    # def predict(self, x):
    #     pred = []
    #     self.models["TEST"].eval()
    #     pred.append(self.models["TEST"](torch.FloatTensor(x.tolist())).detach().numpy()[0])
    #     return pred

    # def save_model(self):
        
    #     if self.target_type and self.TRAIN:
    #         for type in self.target_type:
    #             path = "myPackage/ML/Model/{}/{}".format(self.key, type)
    #             torch.save(self.models[type].state_dict(), path)
    #             self.log_info_signal.emit("\nsave model: {}\n".format(path))

    #         with open("dataset.json", "w") as outfile:
    #             data = {}
    #             data["x_train"] = list(self.x_train)
    #             data["y_train"] = list(self.y_train)
    #             json.dump(data, outfile)

    def __init__(self, loss_plot, PRETRAIN_MODEL=False, TRAIN=True, input_dim=32, output_dim=1):
        self.model =  My_Model(input_dim, output_dim)
        self.loss_plot = loss_plot
        self.PRETRAIN_MODEL = PRETRAIN_MODEL
        self.TRAIN = TRAIN

        self.criterion = nn.MSELoss(reduction='mean')
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-5)
        self.epoch_n=200
        self.train_idx = 1
        self.pred_idx = 3
        self.x_train = []
        self.y_train = []

        if self.PRETRAIN_MODEL and os.path.exists("My_Model"):
            self.model.load_state_dict(torch.load("My_Model"))
            self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-7)
            self.epoch_n=100
            self.train_idx = 5

        

    def train(self):
        train_dataset = My_Dataset(self.x_train, self.y_train)
        bs = 16
        train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=True)
        self.model.train()
        loss_record = []

        for epoch in range(self.epoch_n):
            for x, y in train_loader:
                output = self.model(x)
                loss = self.criterion(output, y)
                # Compute gradient(backpropagation).
                loss.backward()
                # Update parameters.
                self.optimizer.step()
                loss_record.append(loss.detach().item())
            
            if (epoch+1) % 10 == 0:
                mean_train_loss = sum(loss_record)/len(loss_record)
                self.loss_plot.update([mean_train_loss])  # plot loss

    def update_dataset(self, x, y):
        # print(x,y)
        # if (np.abs(y)/self.std_IQM>self.select_threshold).any():
        #     y[np.abs(y)<self.zero_threshold] = 0
        self.x_train.append(x.tolist())
        self.y_train.append(y.tolist())

    def predict(self, x):
        self.model.eval()
        return self.model(torch.FloatTensor(x.tolist())).detach().numpy()

    


    

        