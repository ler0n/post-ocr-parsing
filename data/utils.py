import random
import pandas as pd
import pickle
import re

local_num = ['02','051','053','032', '062','042','052','044','031','033','043','041','063','061','054','055','064','070']
parser_num = [' ','-', '.']
email = ['@gmail.com','@outlook.kr', '@outlook.com', '@hotmail.com', '@icloud.com', '@mac.com', '@me.com', '@naver.com', '@hanmail.net',
        '@daum.net', '@nate.com', '@kakao.com', '@citizen.seoul.kr', '@yahoo.co.jp', '@yahoo.com', '@yandex.com', '@yandex.ru']
id_cand = list('abcdefghizklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')

def email_address():
    id = ''
    n = random.randint(4,15)
    i = 0
    while i!=n:
        id+=random.choice(id_cand)
        i+=1
    return id + random.choice(email)

def h_num(i):
    if random.random()> 0.5:
        return None
    else:
        local = random.choice(local_num)
        tmp = [local, str(random.randint(100,10000)) , str(random.randint(1000,10000))]
        return parser_num[i].join(tmp)
    
def phone_num(i):
    tmp = ['010', str(random.randint(1,10000)).zfill(4) , str(random.randint(1,10000)).zfill(4)]
    return parser_num[i].join(tmp)
            
def name():
    tmp = [random.choice(last_name_list) , random.choice(first_name_list)]
    if random.random()> 0.5:
        return ''.join(tmp)
    return ' '.join(tmp)

def position():
    return random.choice(position_list)

with open("./pickle/first_name_list.pickle","rb") as f:
    first_name_list = pickle.load(f)
with open("./pickle/last_name_list.pickle","rb") as f:
    last_name_list = pickle.load(f)
with open("./pickle/position_list.pickle","rb") as f:
    position_list = pickle.load(f)
    
def random_info():
    i = random.randint(0,2)
    return  h_num(i), phone_num(i), email_address(), name(), position()



