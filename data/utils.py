import random
import pandas as pd
import pickle
import re

local_num = ['02','051','053','032', '062','042','052','044','031','033','043','041','063','061','054','055','064','070']
email = ['@gmail.com','@outlook.kr', '@outlook.com', '@hotmail.com', '@icloud.com', '@mac.com', '@me.com', '@naver.com', '@hanmail.net',
        '@daum.net', '@nate.com', '@kakao.com', '@citizen.seoul.kr', '@yahoo.co.jp', '@yahoo.com', '@yandex.com', '@yandex.ru']
id_cand = list('abcdefghizklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')

def account():
    id = ''
    n = random.randint(5,21)
    i = 0
    while i!=n:
        id+=random.choice(id_cand)
        i+=1
    return id

with open("./pickle/first_name_list.pickle","rb") as f:
    first_name_list = pickle.load(f)
with open("./pickle/last_name_list.pickle","rb") as f:
    last_name_list = pickle.load(f)
with open("./pickle/position_list.pickle","rb") as f:
    position_list = pickle.load(f)
    
def random_info():
    print('TEL:', random.choice(local_num) + ' ' + str(random.randint(100,10000)) + ' ' + str(random.randint(1000,10000)))
    print('핸드폰:','010' + ' ' + str(random.randint(1,10000)).zfill(4) + ' ' + str(random.randint(1,10000)).zfill(4))
    print('이메일:', account() + random.choice(email))
    print('이름:', random.choice(last_name_list) + random.choice(first_name_list))
    print('직책:',random.choice(position_list))



