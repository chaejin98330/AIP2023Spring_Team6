import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import time
import tqdm
from tqdm.notebook import tqdm as notebooktqdm
import matplotlib.pyplot as plt
import pickle
from sklearn.model_selection import train_test_split
from PIL import Image
import timm
from timm.layers import BatchNormAct2d
import os
# from google.colab import files

class EcodingModel(nn.Module):
    def __init__(self):
        super(EcodingModel, self).__init__()
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.feature_map_channel = 320
        self.feature_map_h = 6
        self.feature_map_w = 10

        self.efficient_net_channel1 = 1280
        self.efficient_net_channel2 = 1000

        # image squeezing
        self.img_squeeze_channel1 = self.efficient_net_channel2
        self.img_squeeze_channel2 = 2000
        self.img_squeeze_channel3 = 1000
        self.img_squeeze_channel4 = 500
        self.img_squeeze_channel_out = 100

        # title squeezing
        self.title_feature_channel = 10
        self.title_squeeze_channel1 = 200
        self.title_squeeze_channel2 = 100
        self.title_squeeze_channel3 = 50
        self.title_squeeze_channel_out = 10

        # meta sqeezing
        self.final_squeeze1 = 20
        self.final_squeeze2 = 20
        self.final_squeeze3 = 10
        self.final_squeeze3 = 5
        self.out_channel = 1
        
        # efficient net
        self.effi1 = nn.Conv2d(self.feature_map_channel, self.efficient_net_channel1, kernel_size=(1,1), stride=(1,1), bias=False)
        self.effi2 = nn.BatchNorm2d(self.efficient_net_channel1, eps=0.001, momentum=0.1, affine=True, track_running_stats=True)
        self.effi3 = nn.SiLU(inplace=True)
        self.effi4 = nn.AdaptiveAvgPool2d((1,1))
        self.effi5 = nn.Linear(self.efficient_net_channel1, self.efficient_net_channel2)
        
        # sqeeze img features
        self.img_squeeze_fc1 = nn.Linear(self.img_squeeze_channel1, self.img_squeeze_channel2)
        self.img_squeeze_fc2 = nn.Linear(self.img_squeeze_channel2, self.img_squeeze_channel3)
        self.img_squeeze_fc3 = nn.Linear(self.img_squeeze_channel3, self.img_squeeze_channel4)
        self.img_squeeze_fc_out = nn.Linear(self.img_squeeze_channel4, self.img_squeeze_channel_out)
 
        # sqeeze img and title features
        self.title_squeeze_fc1 = nn.Linear(self.img_squeeze_channel_out+self.title_feature_channel, self.title_squeeze_channel1)
        self.title_squeeze_fc2 = nn.Linear(self.title_squeeze_channel1, self.title_squeeze_channel2)
        self.title_squeeze_fc3 = nn.Linear(self.title_squeeze_channel2, self.title_squeeze_channel3)
        self.title_squeeze_fc_out = nn.Linear(self.title_squeeze_channel3, self.title_squeeze_channel_out)

        # sqeeze whole datas
        self.final_concat_fc1 = nn.Linear(self.title_squeeze_channel_out+2, self.final_squeeze1)
        self.final_concat_fc2 = nn.Linear(self.final_squeeze1, self.final_squeeze2)
        self.final_concat_fc3 = nn.Linear(self.final_squeeze2, self.final_squeeze3)
        self.final_concat_fc_out = nn.Linear(self.final_squeeze3, self.out_channel)
 
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

        self.to(self.device)
    
    def forward(self, feature_map, title, meta):
        feature_map = feature_map.to(self.device)
        title = title.to(self.device)
        meta = meta.to(self.device)

        x = self.effi1(feature_map)
        x = self.effi2(x)
        x = self.effi3(x)
        x = torch.squeeze(self.effi4(x), dim=(2,3))
        x = self.effi5(x)

        x = self.img_squeeze_fc1(x)
        x = self.dropout(x)
        x = self.relu(x)
        x = self.img_squeeze_fc2(x)
        x = self.dropout(x)
        x = self.relu(x)
        x = self.img_squeeze_fc3(x)
        x = self.dropout(x)
        x = self.relu(x)
        x = self.img_squeeze_fc_out(x)
        x = self.dropout(x)
        x = self.relu(x)

        img_title_feature = torch.cat([x, title], dim=1)
        img_title_feature = self.title_squeeze_fc1(img_title_feature)
        img_title_feature = self.dropout(img_title_feature)
        img_title_feature = self.relu(img_title_feature)
        img_title_feature = self.title_squeeze_fc2(img_title_feature)
        img_title_feature = self.dropout(img_title_feature)
        img_title_feature = self.relu(img_title_feature)
        img_title_feature = self.title_squeeze_fc3(img_title_feature)
        img_title_feature = self.dropout(img_title_feature)
        img_title_feature = self.relu(img_title_feature)
        img_title_feature = self.title_squeeze_fc_out(img_title_feature)
        img_title_feature = self.dropout(img_title_feature)
        img_title_feature = self.relu(img_title_feature)

        whole_feature = torch.cat([img_title_feature, meta], dim=1)
        whole_feature = self.final_concat_fc1(whole_feature)
        whole_feature = self.dropout(whole_feature)
        whole_feature = self.relu(whole_feature)
        whole_feature = self.final_concat_fc2(whole_feature)
        whole_feature = self.dropout(whole_feature)
        whole_feature = self.relu(whole_feature)
        whole_feature = self.final_concat_fc3(whole_feature)
        whole_feature = self.dropout(whole_feature)
        whole_feature = self.relu(whole_feature)
        x = self.final_concat_fc_out(whole_feature)
        return x

    def train_(self, epochs, lr, train_loader, valid_loader, save_every):
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=lr)

        self.train_loss = []
        self.valid_loss = []

        best_mse = 1e100
        best_epoch = 1

        train_start = time.time()

        print("Model will be trained on {}\n".format(self.device))

        for epoch in range(1, epochs + 1):
            self.train()
            print("[Epoch {:3d} / {}]".format(epoch, epochs))

            epoch_start = time.time()
            epoch_loss = 0.0
            self.to(self.device)
            #training
            for batch_idx, batch_data in enumerate(notebooktqdm(train_loader, desc="Training")):
                batch_video_id, batch_image, batch_title, batch_meta, batch_target = batch_data
                batch_target = batch_target.to(self.device)
                
                self.optimizer.zero_grad()
                output = self.forward(batch_image, batch_title, batch_meta)
                loss = self.criterion(output, batch_target)
                loss.backward()
                self.optimizer.step()

                epoch_loss += loss.item()

            epoch_end = time.time()
            m, s = divmod(epoch_end - epoch_start, 60)

            epoch_loss /= len(train_loader)
            self.train_loss.append(epoch_loss)
            
            #validation
            with torch.no_grad():
                self.eval()
                true_y, pred_y = self.predict(valid_loader)                
                true_y = torch.FloatTensor(true_y).unsqueeze(dim=1)
                pred_y = torch.FloatTensor(pred_y)
                valid_loss = self.criterion(pred_y, true_y)
                self.valid_loss.append(valid_loss.item())

            print("Train MSE = {:.4f} | Valid MSE = {:.4f}".format(epoch_loss, valid_loss))
            print(f"Train Time: {m:.0f}m {s:.0f}s\n")

            valid_mse = valid_loss.item()
            if best_mse > valid_mse:
                print("=> Best Model Updated : Epoch = {}, Valid MSE = {:.4f}\n".format(epoch, valid_mse))
                best_mse = valid_mse
                best_epoch = epoch
                torch.save(self.state_dict(), "./best_model/best_model.pt")
            else:
                print()

            # save model for every ? epoch
            if (epoch % save_every) == 0:
                torch.save(self.state_dict(),"./model/epoch{}_train{:.4f}_valid{:.4f}.pt".format(epoch, epoch_loss, valid_mse))

        m, s = divmod(time.time() - train_start, 60)
        print("\nTraining Finished...!!")
        print("\nBest Valid MSE : %.2f at epoch %d" % (best_mse, best_epoch))
        print(f"Total Time: {m:.0f}m {s:.0f}s\nModel was trained on {self.device}!")

        torch.save(self.state_dict(),"./model/epoch{}_train{:.4f}_valid{:.4f}.pt".format(epoch, epoch_loss, valid_mse))
    
    def restore(self):
        with open("./best_model/best_model.pt", "rb") as f:
            state_dict = torch.load(f)
        self.load_state_dict(state_dict)

    def predict(self, dataloader):
        self.to(device)
        with torch.no_grad():
            self.eval()
            true_y = []
            pred_y = []
            for batch_video_id, batch_image, batch_title, batch_meta, batch_target in dataloader:
                batch_image = batch_image.to(device)
                batch_title = batch_title.to(device)
                batch_meta = batch_meta.to(device)
                pred = self.forward(batch_image, batch_title, batch_meta)
                true_y.append(batch_target)
                pred_y.append(pred)
            true_y = torch.cat(true_y, dim=0).squeeze().cpu().numpy()
            pred_y = torch.cat(pred_y, dim=0).cpu().numpy()
        return true_y, pred_y #numpy array
