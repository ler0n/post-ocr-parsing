import os
import telnetlib
import pandas as pd
import numpy as np
import pickle
import re
import itertools
from multiprocessing.connection import answer_challenge
import metric
from sklearn import metrics

# 특수문자 제거
def remove_else(input):
    new_string = ''.join(filter(str.isalnum, input))
    if new_string=='':
        new_string='0'
    return new_string
# 텍스트의 높이 반환
def height_of_text(input_all):
    return (max(input_all["bound"][1])-min(input_all["bound"][1]))
# 언어 확인
def isEnglishOrKorean(input):
    k_count = 0
    e_count = 0
    length=len(input)
    for c in input:
        if ord('가') <= ord(c) <= ord('힣'):
            k_count+=1
        elif ord('a') <= ord(c.lower()) <= ord('z'):
            e_count+=1
    if k_count==length:
        return "한국어"  
    elif e_count==length:
        return "영어" 
    elif k_count+e_count>=length-1:
        return 'mixed'
    else:
        return 'else'
# 이름인지 확인
def isname(input,input_original,language,last_name_list,last_name_list_en,first_name_list,height,positionlist):
    # 변수 선언
    cnt=0
    a=0
    answer=0
    # 들어온 값이 직책 리스트에 있으면 제외
    for position_name in positionlist:
        if position_name.lower() == input[-len(position_name):].lower():
            return 0,0,0
    # 특수문자, 괄호, -, 한국어, 영어로 구성되어 있지 않으면, 외장인 경우, 이름 후보에서 제거
    for i in input_original:
        if ((ord('0') <= ord(i) <= ord('9')) 
         or (ord('가') <= ord(i) <= ord('힣'))
         or (ord('a') <= ord(i.lower()) <= ord('z'))
         or ord('A') <= ord(i.lower()) <= ord('Z')
         or i=='-'
         or i==' '
         or i==')'
         or i=='('
        ):
            continue
        else:
            cnt+=1
    if cnt>=1 or len(input)<2:
        return answer,0, 0
    # 언어가 한국어인 경우
    if language=="한국어":
        for last_name in last_name_list:
            if answer!=0:
                break
            if input[0:len(last_name)] == last_name:
                for i in first_name_list:
                    try:
                        # if i == input[len(last_name):len(last_name)+len(i)]:
                        if i == input[len(last_name):]:
                            # answer="1Name: "+input
                            answer=last_name+i
                            break
                    except:
                        continue
    # 언어가 영어인 경우.
    elif language=="영어":
        for last_name_en in last_name_list_en:
            # if last_name_en=="kim":
            # if len(input)>len(last_name_en):
            #     print(input[0:len(last_name_en)] == last_name_list_en)
            #     print(input,len(input),input[0:len(last_name_en)],len(last_name_en),"kim")
            if (input[0:len(last_name_en)] == last_name_en) and len(input)<25:
                # answer="2English name: "+ input
                answer = input
    #혼합되어 있는 경우
    elif language=="mixed":
        if (ord('가') <= ord(input[0]) <= ord('힣')):
            ch='k'
        else:
            ch='e'
        for i in range(len(input)):
            if (ord('가') <= ord(input[i]) <= ord('힣')):
                ch2='k'
            else:
                ch2='e'
            if ch!=ch2:
                # print(ch,ch2,i)
                a=i
                if ch=='k':
                    for last_name in last_name_list:
                        if answer!=0:
                            break
                        if input[0:len(last_name)] == last_name:
                            for i in first_name_list:
                                try:
                                    # if i == input[len(last_name):len(last_name)+len(i)]:
                                    if i == input[len(last_name):]:
                                        # answer="1Name: "+input
                                        answer=last_name+i
                                        break
                                except:
                                    continue
                else:
                    for last_name_en in last_name_list_en:
                        if (input[0:len(last_name_en)] == last_name_en):
                            # print(last_name_en,"last_name_en")
                            # answer="2English name: "+ input[0:i]
                            answer= input[0:i]
                break
    return answer, a, height
# 전화번호인지 확인
def isnum(input):
    # 앞 글자
    a=0
    fax=["fax"]
    tel=["tel","t"]
    phone=["phone","mobile","m"]
    temp=''
    # 앞자리 리스트 만들기
    nat_list=['82']
    phone_list=['010','011','017']
    n_phone_list=[]
    for phone in phone_list:
        temp=phone[1:]
        n_phone_list.append(temp)
    tel_list=['02','051','053','032', '062','042','052','044','031','033','043','041','063','061','054','055','064','070']
    n_tel_list=[]
    for tel in tel_list:
        temp=tel[1:]
        n_tel_list.append(temp)

    # 종류 구분하기
    cat=''
    temp=''
    for c in input:
        if ord('0') <= ord(c) <= ord('9'):
            temp+=c
    for nat_num in nat_list:
        if len(nat_num)<len(temp):
            if nat_num==temp[0:len(nat_num)]:
                if temp[len(nat_num):len(nat_num)+2] in n_phone_list:
                    cat="phone"
                elif temp[len(nat_num):len(nat_num)+2] in n_tel_list or  temp[len(nat_num):len(nat_num)+1]=='02':
                    for fax_str in fax:
                        if fax_str in input:
                            cat="fax"
                            return 0,0
                    else:
                        cat="tel"
    if cat=="":
        if temp[0:3] in phone_list:
            cat="phone"
        elif temp[0:3] in tel_list or temp[0:2]=='02':
            for fax_str in fax:
                # if fax_str in small_input:
                if fax_str in input[0:9]:
                    cat="fax"
                    return 0,0
                # print(temp,small_input)               
            if cat=='':
                cat="tel"
        else:
            return 0, 0   
    
    # 번호면 print, 숫자 아닌 것 연속으로 2개 나오면 끊기
    temp=''
    for c in range(len(input)):
        if ord('0') <= ord(input[c]) <= ord('9'):
            temp+=input[c]
            cnt=0
        elif temp!='' and (ord('0') >= ord(input[c]) or ord(input[c]) >= ord('9')):
            cnt=cnt+1
            if cnt>1:
                a=c-cnt
                break
                # isnum(input[c-2:],input_original[c-2:],1)
    if temp.isdigit()==True and len(temp)<=13 and len(temp)>=9:
        # number="3"+cat+": "+temp
        number = cat+temp
        return number, a
    else:
        return 0, 0
# 직위/직책인지 확인
def isposition(input_original, position_list,language,last_name_list,last_name_list_en,first_name_list,height):
    pos_answer=0
    ans=0
    # 직책 리스트에 있는지 확인
    if language=="한국어":
        for position in position_list:
            if position.lower() == input_original[-len(position):].lower():
                ans, alpha_temp, height = isname(input_original[:-len(position)],input_original[:-len(position)],language,last_name_list,last_name_list_en,first_name_list,height,position_list)
                if ans==0:    
                    pos_answer=input_original
                else:
                    pos_answer=input_original[len(ans):]
                pos_answer=position
                # pos_answer="4Position: " +input_original
    elif language=="영어" or language=="mixed":
        for position in position_list:
            if metric.cer(position.lower(),input_original[-len(position):].lower())<0.2:
                ans, alpha_temp, height = isname(input_original[:-len(position)],input_original[:-len(position)],language,last_name_list,last_name_list_en,first_name_list,height,position_list)
                if ans==0:    
                    pos_answer=input_original[:-len(position)]+position
                else:
                    pos_answer=input_original[len(ans):-len(position)]+position
                pos_answer=position           
    else:
        pass

    return pos_answer,ans
# 이메일인지 확인
def isemail(input_original):
    pos_answer=0
    p=input_original.find('@')
    elist=['email','mail','e-mail']
    # elist_temp=['E','e','Email','emali','EMAIL','mail','Mail','MAIL']
    elist_temp=['E','m','EMAIL','Mail','e-mail']
    email=['@gmail.com','@outlook.kr', '@outlook.com', '@hotmail.com', '@icloud.com', '@mac.com', '@me.com', '@naver.com', '@hanmail.net',
        '@daum.net', '@nate.com', '@kakao.com', '@citizen.seoul.kr', '@yahoo.co.jp', '@yahoo.com', '@yandex.com', '@yandex.ru']
    for i in elist_temp:
        elist.append(i+".")
        elist.append(i+":")
    # 이메일 주변 단어가 있는 경우: cer 적용
    if p==-1:
        for email_ad in email:
            if len(input_original)>len(email_ad):
                if metric.cer(email_ad,input_original[-len(email_ad):])<0.3:
                    for i in elist:
                        if len(input_original)>len(i):
                            if i.lower()==input_original[0:len(i)].lower():
                                pos_answer= input_original[len(i):]
                                # 후처리 x
                    if pos_answer==0:
                        pos_answer=input_original
    # 이메일 주변 단어가 없는 경우
    else:
        for i in elist:
            if len(input_original)>len(i):
                if i.lower()==input_original[0:len(i)].lower():
                    pos_answer= input_original[len(i):]
                    # 후처리 x
        if pos_answer==0:
            pos_answer=input_original
    return pos_answer
# categorize
def categorize_namecard(inputlist,data_all_list,pickle_file,position_list, last_name_list, last_name_list_en, first_name_list):
    # 값 선언
    a=2
    answer_name, answer_number, answer_phone, answer_tel, answer_position, answer_email = [], [], [], [], [], [] 
    left_axis_list=[]
    right_axis_list=[]
    height_list=[]
    input_changed=[]
    catbef=""
    # input 변경한 값 만들기
    for i in range(len(inputlist)):
        temp=remove_else(inputlist[i])
        temp=temp.lower()
        input_changed.append(temp)

    for i in range(len(inputlist)):
        left_axis = data_all_list[i]["bound"][0][0]
        right_axis = data_all_list[i]["bound"][0][1]
        height=height_of_text(data_all_list[i])
        language=isEnglishOrKorean(input_changed[i])

        f=0
        alpha=0 
        chalpha=0
        chbeta=0
        alpha_temp=1
        # position
        postion_candidate, name_candidate = isposition(inputlist[i],position_list,language,last_name_list,last_name_list_en,first_name_list,height)
        if postion_candidate!=0:
            answer_position.append(postion_candidate)
            left_axis_list.append(left_axis)
            right_axis_list.append(right_axis)
            height_list.append(height)
        # call_number
        while f>0 or chbeta==0:
            chbeta=1
            call_number, f = isnum(input_changed[i][f:])
            if call_number!=0:
                answer_number.append(call_number)
                left_axis_list.append(left_axis)
                right_axis_list.append(right_axis)
                height_list.append(height)
        # email
        email_candidate = isemail(inputlist[i])
        if email_candidate!=0:
            check=1
            answer_email.append(email_candidate)
            left_axis_list.append(left_axis)
            right_axis_list.append(right_axis)
            height_list.append(height)
        if postion_candidate==0 and email_candidate==0:
            while alpha_temp>0 or chalpha==0:
                chalpha=1
                if input_changed[i][alpha:]!='':
                    ans, alpha_temp, height = isname(input_changed[i][alpha:],inputlist[i][alpha:],language,last_name_list,last_name_list_en,first_name_list,height,position_list)
                    language = isEnglishOrKorean(input_changed[i][alpha:])
                    if a!=0 and ans!=0:
                        name_with_height=[ans,int(height),int(left_axis),int(right_axis),language]
                        answer_name.append(name_with_height)
                    alpha+=alpha_temp
                else:
                    alpha_temp=0
        if name_candidate!=0:
            language_of_text = isEnglishOrKorean(name_candidate)
            name_with_height=[name_candidate,int(height),int(left_axis),int(right_axis),language_of_text]
            answer_name.append(name_with_height)
    # 축 및 좌표 기준 설정
    left_axis_name_norm=(sum(left_axis_list))/(len(left_axis_list)+0.0000001)
    right_axis_name_norm=(sum(right_axis_list))/(len(right_axis_list)+0.0000001)
    height_norm=sum(height_list)/(len(height_list)+0.0000001)
    # 중복 값에 대한 최종 값 선정
    if answer_name==[]:
        answer_name=['']
    else:
        temp_name=[]
        temp2_name=[]
        for i in range(len(answer_name)):
            min_dis=min(abs(answer_name[i][2]-left_axis_name_norm),abs(answer_name[i][3]-right_axis_name_norm))
            templist=[answer_name[i][0],answer_name[i][1],min_dis,answer_name[i][4]]
            if (len(answer_name[i][0]))>=2 and answer_name[i][1]>height_norm:
                if answer_name[i][4]=='한국어':
                    temp_name.append(templist)
                else:
                    temp2_name.append(templist)
        answer_name=temp_name
        answer2_name=temp2_name
        answer_name=sorted(answer_name, key=lambda x: (x[2],-x[1]))
        answer2_name=sorted(answer_name, key=lambda x: (x[2],-x[1]))
        answer_name=answer_name+answer2_name
        if answer_name==[]:
            answer_name=['']
        else: 
            answer_name=[answer_name[0][0]]
    if answer_position==[]:
        answer_position=['']
    else:
        answer_position=[answer_position[0]]

    if answer_email==[]:
        answer_email=['']
    else:
        for i in answer_email:
            if '@' in i:
                answer_email=[i]
            else:
                answer_email=[answer_email[0]]
    for i in answer_number:
        if "phone" in i:
            answer_phone.append(str(i[5:]))
        elif "tel" in i:
            answer_tel.append(str(i[3:]))
    if answer_tel==[]:
        answer_tel=['']
    else:
        answer_tel=[answer_tel[0]]
    if answer_phone==[]:
        answer_phone=['']
    else:
        answer_phone=[answer_phone[0]]

    answer_f=[pickle_file]
    predict=(
        answer_f
        +answer_name
        +[""]
        +answer_tel
        +answer_phone
        +answer_email
        +answer_position
        )
    return predict
# F1 score 계산
def metric_namecard(y_true, y_pred):
    y_pred_name, y_true_name=[], []
    y_pred_en_name ,y_true_en_name=[], []
    y_pred_tel, y_true_tel=[], []
    y_pred_phone, y_true_phone=[], []
    y_pred_email, y_true_email=[], []
    y_pred_position, y_true_position=[], []

    for i in range(len(y_true)):
        if i%6==0:
            y_pred_name.append(y_pred[i])
            y_true_name.append(y_true[i])
        elif i%6==1:
            y_pred_en_name.append(y_pred[i])
            y_true_en_name.append(y_true[i])
        elif i%6==2:
            y_pred_tel.append(y_pred[i])
            y_true_tel.append(y_true[i])
        elif i%6==3:
            y_pred_phone.append(y_pred[i])
            y_true_phone.append(y_true[i])
        elif i%6==4:
            y_pred_email.append(y_pred[i])
            y_true_email.append(y_true[i])
        elif i%6==5:
            y_pred_position.append(y_pred[i])
            y_true_position.append(y_true[i])
    score_name=metrics.f1_score(y_true_name,y_pred_name)
    score_en_name=metrics.f1_score(y_true_en_name,y_pred_en_name)
    score_tel=metrics.f1_score(y_true_tel,y_pred_tel)
    score_phone=metrics.f1_score(y_true_phone,y_pred_phone)
    score_email=metrics.f1_score(y_true_email,y_pred_email)
    score_position=metrics.f1_score(y_true_position,y_pred_position)
    return score_name,score_en_name,score_tel,score_phone, score_email,score_position
# main
def main():
    print("start")
    # 초기 설정(파일 경로)
    RES_PATH = 'res_real_img'
    # RES_PATH = 'res_making_img'
    ANSWER_PATH = 'data_answer'
    ANSWER_FILENAME='real_data2.csv'
    # ANSWER_FILENAME='testset_121.csv'
    IMG_PATH = 'real_img'
    # IMG_PATH = 'making_img'

    file_list = os.listdir(IMG_PATH)
    file_list_img = [file for file in file_list if file.split('.')[-1] in ['jpg', 'png', 'jpeg']]
    pickle_file_list = os.listdir(RES_PATH)
    pickle_file_list_img = [file for file in pickle_file_list if file.split('.')[-1] in ['pickle']]
    # pickle_file_list_img=pickle_file_list_img[0:10]

    # 파일 불러오기
    with open("./pickle/last_name_list.pickle","rb") as f:
        last_name_list = pickle.load(f)
    with open("./pickle/first_name_list.pickle","rb") as f:
        first_name_list = pickle.load(f)
    with open("./pickle/last_name_list_en.pickle","rb") as f:
        last_name_list_en_temp = pickle.load(f)
    with open("./pickle/position_list.pickle","rb") as f:
        position_list = pickle.load(f)
    last_name_list=sorted(last_name_list, key=lambda x: -len(x))
    first_name_list=sorted(first_name_list, key=lambda x: -len(x))
    last_name_list_en=[]
    for i in last_name_list_en_temp:
        a=i.lower()
        last_name_list_en.append(a)
    
    # OCR_value 불러오기
    predict_list=[]
    for pickle_file in pickle_file_list_img:
        res_file = os.path.join(RES_PATH, pickle_file)
        with open(res_file,"rb") as fr:
            data = pickle.load(fr)
        data_list=data["text_list"]
        data_all_list=data["all"]
        predict=categorize_namecard(data_list,data_all_list, pickle_file ,position_list, last_name_list, last_name_list_en, first_name_list)

        predict_list.append(predict)

    # answerfile 불러오기
    answer_file=pd.read_csv(os.path.join(ANSWER_PATH, ANSWER_FILENAME),dtype=str)
    answer_file=answer_file.replace(np.nan, '', regex=True)
    answer=[]
    cnt=0
    for i in file_list_img:
        answer_temp=answer_file.loc[answer_file['file_name']==i]
        answer_temp=list(itertools.chain(*answer_temp.values.tolist()))
        answer.append(answer_temp)
    print("Answer_list complete")

    ### CER 기반 F1 score 계을 위한 y_pred, y_true 계산

    cer_norm=0.2
    y_pred=[]
    y_true=[]

    for i in range(len(predict_list)):
        for j in range(len(answer)):
            if predict_list[i][0]==(answer[j][6]+"_res.pickle"):
                for k in range(0,6):
                    if len(answer[j][k].replace(' ', ''))!=0:
                        cnt+=1
                        cer_value=metric.cer(answer[j][k],predict_list[i][k+1])
                    else:
                        cer_value=1
                    if answer[j][k]!="":
                        y_true.append(1)
                    else:
                        y_true.append(0)
                    if cer_value<=cer_norm:
                        y_pred.append(1)
                    else:
                        y_pred.append(0)
    score_name,score_en_name,score_tel,score_phone, score_email,score_position = metric_namecard(y_true, y_pred)
    print(score_name,score_en_name,score_tel,score_phone, score_email,score_position)

if __name__ == '__main__':
    main()