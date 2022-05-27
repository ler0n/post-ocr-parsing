import os
import telnetlib
import pandas as pd
import numpy as np
import pickle
import re
import itertools
from multiprocessing.connection import answer_challenge
import metric
RES_PATH = 'res2'
ANSWER_PATH = 'dataans'
IMG_PATH = 'img'
file_list = os.listdir(IMG_PATH)
file_list_img = [file for file in file_list if file.split('.')[-1] in ['jpg', 'png', 'jpeg']]
pickle_file_list = os.listdir(RES_PATH)
pickle_file_list_img = [file for file in pickle_file_list if file.split('.')[-1] in ['pickle']]
a=pickle_file_list_img[0]

res_file = os.path.join(RES_PATH, '1006.jpg_res.pickle')
with open(res_file,"rb") as fr:
    data = pickle.load(fr)
data_list=data["all"]
print(data_list)
# print(data,"data")
print(max(data_list[1]["bound"][1])-min(data_list[1]["bound"][1]))