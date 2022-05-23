import random
import pandas as pd
import pickle
import re
import time
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
from utils import *

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

def get_logo_pos(k, Xdim, Ydim, new_logo_x):
    y_gap = random.choice([0.2, 0.25, 0.3, 0.35])
    if k==0:
        return (int(Xdim * 0.1), int(Ydim * y_gap))
    elif k==1:
        return (int(Xdim * 1)-new_logo_x, int(Ydim * y_gap))

def get_necessary_pos(k, Xdim, Ydim, nameFont, name, infoFont, division):
    postions = []
    y_gap = random.choice([0.3, 0.35, 0.4]); 
    y_interval = 0.12
    info_ = [name, division]
    font_ = [nameFont, infoFont]
    ind_ = [0,1]
    random.shuffle(ind_)
    if k==0:
        for i in ind_:
            postions.append((int(Xdim * 0.9 - font_[i].getsize(info_[i])[0]), int(Ydim * y_gap - font_[i].getsize(info_[i])[1])))
            y_gap += y_interval
    elif k==1:
         for i in ind_:
            postions.append((int(Xdim * 0.1), int(Ydim * y_gap - font_[i].getsize(info_[i])[1])))
            y_gap += y_interval
    return postions, [info_[ind_[0]],info_[ind_[1]]], [font_[ind_[0]],font_[ind_[1]]]

def get_optional_pos(k, Xdim, Ydim, optionalFont, telephone, cellphone, e_mail):
    postions = []
    y_gap = random.choice([0.6, 0.65, 0.7]) 
    y_interval = 0.07
    info_ = [info for info in [telephone, cellphone, e_mail] if info!=None]
    random.shuffle(info_)
    if k==0:
        for info in info_:
            postions.append((int(Xdim * 0.9 - optionalFont.getsize(info)[0]), int(Ydim * y_gap - optionalFont.getsize(info)[1])))
            y_gap += y_interval
    elif k==1:
        for info in info_:
            postions.append((int(Xdim * 0.1), int(Ydim * y_gap - optionalFont.getsize(info)[1])))
            y_gap += y_interval
    return postions, info_

def get_other_pos(k, Xdim, Ydim, otherFont, other1, other2):
    postions = []
    y_gap = 0.05; y_interval = 0.9
    info_ = [other1, other2]
    random.shuffle(info_)
    if k==0:
        for info in info_:
            postions.append((int(Xdim * 0.95 - otherFont.getsize(info)[0]), int(Ydim * y_gap - otherFont.getsize(info)[1])))
            y_gap += y_interval
    elif k==1:
        for info in info_:
            postions.append((int(Xdim * 0.05), int(Ydim * y_gap - otherFont.getsize(info)[1])))
            y_gap += y_interval
    return postions, info_

def get_fonts(font_path):
    font_list = os.listdir(font_path)
    font_file = random.choice(font_list)
    font_filename = os.path.join(font_path, font_file)
    return font_filename

def make_namecard_h(args):
    
    print("Process Start.")
    
    logo_list = [x for x in os.listdir(args.logo_path) if x.endswith('.PNG')]
    
    start_time = time.time()
    for _ in range(args.num):
        # 0: 로고 왼쪽, 1: 로고 오른쪽
        k = random.choice([0,1])
        
        logo_file = random.choice(logo_list)
        logo_filename = os.path.join(args.logo_path, logo_file)

        # 명함에 삽입할 회사 정보
        other1 = "다른 내용이 들어갈 수 있는 자리 2"
        other2 = "다른 내용이 들어갈 수 있는 자리 1"

        # 로고 파일 불러오기
        logo = Image.open(logo_filename)
        logo_x, logo_y = logo.size

        # 명함 해상도 지정
        Xdim = 1032
        Ydim = 624

        # 로고 크기를 명함에 삽입하기 좋게 편집합니다. 명함은 세로가 짧으니 세로 길이를 기준으로 작업합니다.
        # 로고의 높이를 명함 높이의 30%로 조절합니다.
        new_logo_y = min(int(Ydim * 0.3),logo_y)
        # 로고의 x축 길이는 비례식으로 계산합니다.
        # new_logo_y : logo_y = new_logo_x : logo_x
        new_logo_x = int(logo_x * (new_logo_y / logo_y))

        resized_logo = logo.resize((new_logo_x, new_logo_y))

        logo.close()

        # 인적사항을 한줄씩 읽어오면서, 한 번에 명함을 한 장씩 만들겁니다.
        # 명함에 들어갈 정보들만 추출합니다.
        telephone, cellphone, e_mail, name, division = random_info()

        # 명함을 저장할 텅빈 템플릿 이미지 생성
        image = Image.new("RGBA", (Xdim, Ydim), "white")

        # 폰트 지정
        # 이름
        nameFont = ImageFont.truetype(get_fonts(args.font_path), 60)
        # URL과 주소
        otherFont = ImageFont.truetype(get_fonts(args.font_path), 40)
        # 직책 정보
        infoFont = ImageFont.truetype(get_fonts(args.font_path), 40)
        # 나머지 정보
        optionalFont = ImageFont.truetype(get_fonts(args.font_path), 30)


        logo_pos = get_logo_pos(k, Xdim, Ydim, new_logo_x)
        necessary_pos, necessary_info, necessary_font = get_necessary_pos(k, Xdim, Ydim, nameFont, name, infoFont, division)
        optional_pos, optional_info = get_optional_pos(k, Xdim, Ydim, optionalFont, telephone, cellphone, e_mail)
        other_pos, other_info = get_other_pos(k, Xdim, Ydim, otherFont, other1, other2)

        # 여백 10% 주고 로고 삽입
        image.paste(resized_logo, logo_pos)

        resized_logo.close()
        # 기타 정보를 삽입합니다.
        # ImageFont.getsize()의 반환값은 (길이,높이)
        for info, pos in zip(other_info, other_pos):
            ImageDraw.Draw(image).text(xy=pos, text=info, font=optionalFont, fill="black")

        # 명함 템플릿을 복제합니다.
        namecard = image.copy()

        for info, pos, font in zip(necessary_info, necessary_pos, necessary_font):
            ImageDraw.Draw(namecard).text(xy=pos, text=info, font=font, fill="black")

        # 부가 정보를 삽입합니다.
        for info, pos in zip(optional_info, optional_pos):
            ImageDraw.Draw(namecard).text(xy=pos, text=info, font=optionalFont, fill="black")

        # 완성된 명함을 저장합니다.
        namecard.save(args.out_dir + "/" + division + "_" + name  + ".png")

        namecard.close()

        image.close()
        
    print(f"Process Done: {args.num}개 명함 생성 완료")
    end_time = time.time()
    print("The Job Took " + str(end_time - start_time) + " seconds.")

    return

