import os
import telnetlib
from tempfile import tempdir
import pandas as pd
import numpy as np
import pickle
import re
import itertools
from multiprocessing.connection import answer_challenge
import metric

RES_PATH = 'res3'
ANSWER_PATH = 'dataans'
IMG_PATH = 'img_R2'
answer_file=pd.read_csv(os.path.join(ANSWER_PATH, 'namelist.csv'),dtype=str)
answer_file=answer_file.replace(np.nan, '', regex=True)
answer=[]
cnt=0
cer_value_sum=0
file_list = os.listdir(IMG_PATH)
file_list_img = [file for file in file_list if file.split('.')[-1] in ['jpg', 'png', 'jpeg']]
print(file_list_img)
for i in range(len(file_list_img)):
    file_oldname = os.path.join(IMG_PATH,file_list_img[i])
    temp= "real_"+"0"*(4-len(str(i+32)))+str(i+31)+file_list_img[i][file_list_img[i].find("."):] 
    file_newname_newfile = os.path.join(IMG_PATH,temp)
    print(file_oldname,file_newname_newfile)
    os.rename(file_oldname, file_newname_newfile)
print(file_list_img)
for i in file_list_img:
    answer_temp=answer_file.loc[answer_file['image_name']==i]
    answer_temp=list(itertools.chain(*answer_temp.values.tolist()))
    answer.append(answer_temp)
print(answer)