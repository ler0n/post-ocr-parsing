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
from pandas.core.common import flatten
from faker import Faker
import zipfile
import shutil
import urllib
from urllib import parse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

# 전화번호, 팩스번호의 parser와 지역번호, 국제번호
local_num = ['02','051','053','032', '062','042','052','044','031','033','043','041','063','061','054','055','064','070', '0507']
global_num = ['82', '+82','(82)', '(+82)']
parser_num = [' ','-', '.', '']

# 소속의 뒷부분
paser_pos = ['/', '|']
team_kor = ['실', '팀', '과', '부']
team_eng = ['Team', 'Dept.', 'Department','Section', 'Office']

# email의 도메인주소와 아이디 랜덤 추출 후보
email = ['@gmail.com','@outlook.kr', '@outlook.com', '@hotmail.com', '@icloud.com', '@mac.com', '@me.com', '@naver.com', '@hanmail.net',
        '@daum.net', '@nate.com', '@kakao.com', '@citizen.seoul.kr', '@yahoo.co.jp', '@yahoo.com', '@yandex.com', '@yandex.ru']
id_cand = list('abcdefghizklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.')

# 전화번호, 핸드폰번호, 이메일, 팩스의 header
optional_heads = [['','','',''],['','','',''],['','','',''],['','','',''],['','','',''],
                  ['T.', 'M.', 'E.', 'F.'], ['Tel.', 'Mobile.', 'Email.', 'Fax.'], ['tel.', 'mob.', 'mail.', 'fax.'],['t.', 'm.', 'e.', 'f.'],
                 ['T:', 'M:', 'E:','F:'], ['Tel:', 'Mobile:', 'Email:','Fax:'], ['tel:', 'mob:', 'mail:','fax:'],['t:', 'm:', 'e:','f:'],
                  ['T_', 'M_', 'E_','F_'], ['Tel_', 'Mobile_', 'Email_','Fax_'], ['tel_', 'mob_', 'mail_','fax_'],['t_', 'm_', 'e_','f_'],
                 ['T. ', 'M. ', 'E. ', 'F. '], ['Tel. ', 'Mobile. ', 'Email. ', 'Fax. '], ['tel. ', 'mob. ', 'mail. ', 'fax. '],['t. ', 'm. ', 'e. ', 'f. '],
                 ['T: ', 'M: ', 'E: ', 'F: '], ['Tel: ', 'Mobile: ', 'Email: ', 'Fax: '], ['tel: ', 'mob: ', 'mail: ', 'fax: '],['t: ', 'm: ', 'e: ', 'f: ']]

fake = Faker("ko_KR")
bio_tag = {0: 'TEL', 1:'FAX', 2: 'NUM', 3:'MAIL', 4: 'PER', 5:'POS', 6: 'ADD', 7:'PER_E'}

# pickle에 보관한 명함 내의 정보 불러오기
with open("./pickle/first_name_list.pickle","rb") as f:
    first_name_list = pickle.load(f)
with open("./pickle/last_name_list.pickle","rb") as f:
    last_name_list = pickle.load(f)
with open("./pickle/position_list.pickle","rb") as f:
    position_list = pickle.load(f)
    team_list = pickle.load(f)
with open("./pickle/company_list.pickle","rb") as f:
    company_list = pickle.load(f)

# 전화번호, 팩스번호의 앞 번호의 괄호 여부를 결정
def local_style(num):
    if random.random()> 0.5:
        return num
    elif random.random()> 0.5:
        return num + ')'
    else:
        return '(' + num + ')'

# 아래 정보 생성 함수들은 생성 정보와 정답 label을 tuple 쌍으로 생성(정답 label이 없는 주소, 웹주소 등 제외)
    
# 도메인 주소의 무작위 추출과 아이디 무작위 생성을 통한 이메일 주소 생성
def email_address(heads):
    id = ''
    n = random.randint(4,15)
    i = 0
    while i!=n:
        id+=random.choice(id_cand)
        i+=1
    label = id + random.choice(email)
    return (heads[2]  + label, label) 

# 지역번호를 골라 전화번호 생성, 일정 확률로 국제번호로 생성
def ph_num(i, heads):
    if random.random()> 0.5:
        return (None, '')
    mid = str(random.randint(100,10000))
    last = str(random.randint(1000,10000))
    if random.random()> 0.2:
        local = random.choice(local_num)
        label = local + mid + last
        tmp = [local_style(local), mid , last]
    else:
        local = random.choice(local_num)
        label = '82' + local + mid + last
        tmp = [random.choice(global_num) ,local_style(local)[1:], mid , last]
    
    return (heads[0]  + parser_num[i].join(tmp), label)

# 지역번호를 골라 팩스번호 생성, 일정 확률로 국제번호로 생성
def fax_num(i, heads):
    if not heads[3]:
        return (None, '')
    mid = str(random.randint(100,10000))
    last = str(random.randint(1000,10000))
    if random.random()> 0.2:
        local = random.choice(local_num)
        label = local + mid + last
        tmp = [local_style(local), mid , last]
    else:
        local = random.choice(local_num)
        label = '82' + local + mid + last
        tmp = [random.choice(global_num) ,local_style(local)[1:], mid , last]
    
    return (heads[3]  + parser_num[i].join(tmp), label)

# 핸드폰번호 생성, 일정 확률로 국제번호로 생성
def mob_num(i, heads):
    if random.random() > 0.2:
        tmp = ['010', str(random.randint(1,10000)).zfill(4) , str(random.randint(1,10000)).zfill(4)]
        label = ''.join(tmp)
    else:
        tmp = [random.choice(global_num), '10', str(random.randint(1,10000)).zfill(4) , str(random.randint(1,10000)).zfill(4)]
        label = '82' + ''.join(tmp[1:])            
    return (heads[1]  + parser_num[i].join(tmp), label)
            
# 이름 생성, pickle에서 불러온 성과 이름 정보 활용
def name():
    tmp = [random.choice(last_name_list) , random.choice(first_name_list)]
    label = ''.join(tmp)
    if random.random()< 0.67:
        name = ''.join(tmp)
        if random.random()> 0.5:
            name = ' '.join(list(name))
        return name, label
    return ' '.join(tmp), label

# 소속 + 직책 생성
# 소속의 경우 pickle에서 불러온 소속 정보 + 위에서 정의한 붙을 수 있는 팀 이름으로, 한글과 영어 둘 중 하나로 생성
def position():
    team = random.choice(team_list)
    p = re.compile('[a-zA-Z& ]+')
    try:
        if re.match(p, team).group()==team:
            team += ' ' + random.choice(team_eng)
        else:
            team += random.choice(team_kor)
    except:
        team += random.choice(team_kor)
    return team + ' ' + random.choice(paser_pos) + ' ' + random.choice(position_list)
    
# 위에서 정의한 함수들을 활용해 명함에 들어갈 정보를 생성
# 정보와 정답 label을 튜플 쌍으로 생성
def random_info(i, heads):
    phone_num, phone_label = ph_num(i,heads)
    mobile_num, mobile_label = mob_num(i, heads)
    email_add, email_label = email_address(heads)
    name_, name_label = name()
    pos = position()
    if '|' in pos:
        pos_label = pos.split('|')[-1].strip()
    else:
        pos_label = pos.split('/')[-1].strip()
    fax_ , fax_label= fax_num(i, heads)
    address = get_address()
    
    return (phone_num, fax_, mobile_num, email_add, name_, pos, address), (name_label, email_label, phone_label, fax_label, mobile_label, pos_label, address)

# 한글 이름을 네이버 변환기에서 변환 후 무작위 하나 추출하여 영어 이름 생성
# 너무 많은 명함을 한 번에 생성하는 경우 504 Gateway Timeout 발생하는 경우 있음(10000개 시도시 에러 자주 발생)
def get_english_name(name):
    naver_url = 'https://dict.naver.com/name-to-roman/translation/?query='
    name_url = naver_url + urllib.parse.quote(name)

    req = Request(name_url)
    res = urlopen(req)

    html = res.read().decode('utf-8')
    bs = BeautifulSoup(html, 'html.parser')
    name_tags = bs.select('#container > div > table > tbody > tr > td > a')
    names = [name_tag.text for name_tag in name_tags]

    name_eng = ''
    if names:
        name_eng = random.choice(names)
        name_eng = name_eng.split()
        random.shuffle(name_eng)
        name_eng = ' '.join(name_eng)
    return name_eng
    
# Faker 모듈을 이용해 주소 생성
# 뒤쪽에 붙는 주소는 수집 명함의 표본을 바탕으로 추가함
def get_address():
    address = fake.address()
    road = str(random.randint(1,100)) + '길'
    num_address = str(random.randint(1,10000)) 
    if random.random() > 0.5:
        num_address += ('-' + str(random.randint(1,10)))
    if random.random() > 0.5:
        road += ' ' + num_address
    if random.random() > 0.8:
        road += ' ' + random.choice([str(random.randint(1,10)) + random.choice(['층','F']), str(random.randint(101,10000)) + '호'])
    return address + ' ' + road


# 아래의 위치 정보 생성 함수들은 명함에 각 정보들이 위치할 시작 좌표를 지정
# k=0일 때: 로고 왼쪽, 이름 등 정보 오른쪽
# k=1일 때: 로고 오른쪽, 이름 등 정보 왼쪽

# 로고 위치 생성
def get_logo_pos(k, Xdim, Ydim, new_logo_x):
    y_gap = random.choice([0.2, 0.25])
    if k==0:
        return (int(Xdim * 0.1), int(Ydim * y_gap))
    elif k==1:
        return (int(Xdim * 1)-new_logo_x, int(Ydim * y_gap))

# 필수 정보인 이름과 소속+직책 위치 지정
# 글씨의 크기와 양을 고려해 배치하기 때문에 폰트가 인자로 필요
def get_necessary_pos(k, Xdim, Ydim, nameFont, name, infoFont, position):
    postions = []
    y_gap = random.choice([0.3, 0.35]); 
    y_interval = 0.12
    info_ = [name, position]
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

# 부가 정보인 전화번호, 핸드폰번호, 이메일, 팩스번호, 주소 위치 지정
# 글씨의 크기와 양을 고려해 배치하기 때문에 폰트가 인자로 필요
def get_optional_pos(k, Xdim, Ydim, optionalFont, telephone, cellphone, e_mail, fax, address):
    postions = []
    y_gap = 0.6 
    y_interval = 0.07
    # 전화번호와 팩스번호는 존재하지 않도록 한 경우가 있어 예외처리
    info_ = [info for info in [telephone, cellphone, e_mail, fax, address] if info!=None]
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

# 기타 정보인 영어이름과 (회사명 + 웹주소) 위치 지정
# 글씨의 크기와 양을 고려해 배치하기 때문에 폰트가 인자로 필요
# 각각 명함의 맨 위와 아래에 위치
def get_other_pos(k, Xdim, Ydim, otherFont, name_eng, other2):
    postions = []
    y_gap = 0.05; y_interval = 0.9
    info_ = [name_eng, other2]
    if k==0:
        for info in info_:
            postions.append((int(Xdim * 0.95 - otherFont.getsize(info)[0]), int(Ydim * y_gap - otherFont.getsize(info)[1])))
            y_gap += y_interval
    elif k==1:
        for info in info_:
            postions.append((int(Xdim * 0.05), int(Ydim * y_gap - otherFont.getsize(info)[1])))
            y_gap += y_interval
    return postions, info_


# 폰트 저장 폴더에서 무작위 추출
def get_fonts(font_path):
    font_list = os.listdir(font_path)
    font_file = random.choice(font_list)
    font_filename = os.path.join(font_path, font_file)
    return font_filename

# 정답 label text 파일에 기록
def add_label(args, labels):
    version = str(args.version).zfill(2)
    labels = ','.join(labels)
    with open(os.path.join(args.label_path, f"label_v.{version}.txt"), "a") as f:
        f.write(f'{labels}')
        f.write("\n")
    return

# BIO tag text 파일에 기록
def add_BIO_tags(args, file_name, informations, bio_tag):
    version = str(args.version).zfill(2)
    text = []
    bio_tags = []
    for i, info in enumerate(informations):
        if info:
            tmp = info.split()
            text.append(tmp)
            # 직책의 경우 소속과 함께 들어 있기 때문에 예외처리
            if i<8 and bio_tag[i]!='POS':
                bio_tags.append([bio_tag[i]+'-B']+[bio_tag[i]+'-I']*(len(tmp)-1))
            elif i<8 and bio_tag[i]=='POS':
                for x in paser_pos:
                    if x in tmp:
                        t = tmp.index(x)
                        bio_tags.append(['O']*(t+1) + [bio_tag[i]+'-B'] +[bio_tag[i]+'-I']*(len(tmp)-t-2))         
            else:
                bio_tags.append(['O']*(len(tmp)))
    tmp = list(zip(text, bio_tags))
    random.shuffle(tmp)
    text, bio_tags = zip(*tmp)
    text = list(flatten(text))
    bio_tags = list(flatten(bio_tags))
    info_ = ' '.join(text)
    tags_ = ' '.join(bio_tags)
    with open(os.path.join(args.label_path, f"BIO_tags_v.{version}.txt"), "a") as f:
        f.write(f'{file_name}' + '\t' + f'{info_}' + '\t' + f'{tags_}')
        f.write("\n")
    
    return text, bio_tags
    
# 명함 num개 생성(namecards.py 실행 시 개수 지정)
def make_namecard_h(args):
    
    print("Process Start.")
    
    # 이미 생성한 명함이 저장 폴더에 남아있는 경우 삭제
    shutil.rmtree(args.out_dir)
    os.mkdir(args.out_dir)
    cnt = len(os.listdir(args.out_dir))
    
    # logo.zip 파일 압축 해제
    logo_zip = zipfile.ZipFile(os.path.join(args.logo_path, args.logo_images))
    logo_zip.extractall(args.logo_path)
    logo_zip.close()
    
    # logo에 포함된 텍스트를 BIO tagging에 포함시키기 위해 logo.csv에 로고의 텍스트 정보를 따로 저장해두어야 함
    df_logo = pd.read_csv(os.path.join(args.logo_path, "logo.csv"))
    logo_list = df_logo['name']
    logo_texts = {logo_file_name:text for logo_file_name, text in zip(logo_list, df_logo['logo'])}
    
    start_time = time.time()
    for _ in range(args.num):
        # 0: 로고 왼쪽, 1: 로고 오른쪽
        k = random.choice([0,1])
        i = random.randint(0,len(parser_num)-1)
        # cnt: naming용
        cnt +=1
        file_path = os.getcwd() + "/namecards/" + "gen_" + str(cnt).zfill(5)  + ".png"
        
        heads = random.choice(optional_heads)
        
        logo_file = random.choice(logo_list)
        logo_text = logo_texts[logo_file]
        logo_filename = os.path.join(args.logo_path, logo_file)

        # 주소, fax
        address = get_address()
        fax = fax_num(i, heads)
        
        # 명함에 삽입할 회사 정보
        # other2 = get_address()
        other1 = random.choice(company_list) + ' ' + random.choice(['/', '|', '_']) + ' ' +random.choice(fake.profile()['website'])

        # 로고 파일 불러오기
        logo = Image.open(logo_filename)
        logo_x, logo_y = logo.size

        # 명함 해상도(크기) 지정
        Xdim = 1032
        Ydim = 624

        # 로고 크기를 명함에 삽입하기 좋게 편집. 명함은 세로가 짧으니 세로 길이를 기준으로 작업.
        # 로고의 높이를 명함 높이의 30%로 조절
        new_logo_y = min(int(Ydim * 0.3),logo_y)
        # 로고의 x축 길이는 비례식으로 계산합니다.
        # new_logo_y : logo_y = new_logo_x : logo_x
        new_logo_x = int(logo_x * (new_logo_y / logo_y))

        resized_logo = logo.resize((new_logo_x, new_logo_y))

        logo.close()

        # 명함에 들어갈 정보들 추출
        informations, labels = random_info(i, heads)
        # 영어 이름 설정
        name_eng = get_english_name(informations[4])
        other2 = name_eng
        
        informations = list(informations) + [other2, other1, logo_text]
        file_name = file_path.split('/')[-1]
        labels = [file_name] + list(labels)
        add_BIO_tags(args, file_name, informations, bio_tag)
        
        telephone, fax_number, cellphone, e_mail, name, position, address, *_ = informations
        
        labels[1] = labels[1] + '(' + name_eng + ')'
        add_label(args, labels)
        # 명함을 저장할 텅빈 템플릿 이미지 생성
        image = Image.new("RGBA", (Xdim, Ydim), "white")

        # 폰트 지정 - 변경하는 경우에는 위치 지정 함수들의 줄 간격에도 신경써야함
        # 이름
        nameFont = ImageFont.truetype(get_fonts(args.font_path), 55)
        # URL과 주소
        otherFont = ImageFont.truetype(get_fonts(args.font_path), 30)
        # 직책+소속
        infoFont = ImageFont.truetype(get_fonts(args.font_path), 25)
        # 나머지 정보
        optionalFont = ImageFont.truetype(get_fonts(args.font_path), 30)


        # 필요한 위치 정보들 가져오기
        logo_pos = get_logo_pos(k, Xdim, Ydim, new_logo_x)
        necessary_pos, necessary_info, necessary_font = get_necessary_pos(k, Xdim, Ydim, nameFont, name, infoFont, position)
        optional_pos, optional_info = get_optional_pos(k, Xdim, Ydim, optionalFont, telephone, cellphone, e_mail, fax_number, address)
        other_pos, other_info = get_other_pos(k, Xdim, Ydim, otherFont, other1, other2)

        # 여백 10% 주고 로고 삽입
        image.paste(resized_logo, logo_pos)

        resized_logo.close()
        # 기타 정보를 삽입
        # ImageFont.getsize()의 반환값은 (길이,높이)
        for info, pos in zip(other_info, other_pos):
            ImageDraw.Draw(image).text(xy=pos, text=info, font=optionalFont, fill="black")

        # 명함 템플릿을 복제(동일한 템플릿을 가지지만 다른 정보를 가지는 여러 명함을 만들기 위해 필요)
        namecard = image.copy()

        # 필수 정보(이름, 소속+직책) 삽입
        for info, pos, font in zip(necessary_info, necessary_pos, necessary_font):
            ImageDraw.Draw(namecard).text(xy=pos, text=info, font=font, fill="black")

        # 부가 정보(전화번호, 핸드폰번호, 이메일, 팩스번호, 주소) 삽입
        for info, pos in zip(optional_info, optional_pos):
            ImageDraw.Draw(namecard).text(xy=pos, text=info, font=optionalFont, fill="black")

        # 완성된 명함을 저장
        namecard.save(file_path)

        namecard.close()

        image.close()
        
    print(f"Process Done: {args.num}개 명함 생성 완료")
    
    # 생성한 namecards 압축    
    with zipfile.ZipFile( f'dataset_v.{str(args.version).zfill(2)}.zip', 'w') as namecards_zip:
        for file in os.listdir(args.out_dir):
            if not file.endswith('ipynb_checkpoints') or not file.endswith('zip'):
                namecards_zip.write(os.path.join(args.out_dir, file))

    
    
    end_time = time.time()
    print("The Job Took " + str(end_time - start_time) + " seconds.")

    return

