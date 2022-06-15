from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import grouping
import re
import os
import time
import torch
from transformers import BertForTokenClassification
import model.rulebase.rule_base as rule
import model.kobert.all as kobert
from model.kobert.tokenization_kobert import KoBertTokenizer

global img_path, response, card_info


def get_bbox(words: dict):
    bbox = []
    target = ['이름', '이름(en)', '직책', '이메일', 'TEL', 'Mobile']
    for word, t in zip(words, target):
        if words[word]['bbox'] != [] and t != '이름(en)':
            bbox.append((words[word]['bbox'], t))
    return bbox

def get_only_num(input :str):
    ob = re.sub(r'[^0-9]', '', input)
    return ob

def get_mail(input :str):
    regex = re.compile(r"[^ㄱ-ㅎ|가-힣]")
    mail_text = ''.join(regex.findall(input))
    return mail_text


app = FastAPI()
templates = Jinja2Templates(directory="template/")
app.mount("/static", StaticFiles(directory="static"), name="static")
path = "" # /static/index.js의 TextDownload()가 로컬에 저장되는 위치


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = BertForTokenClassification.from_pretrained('model/kobert/model')
tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert')
model.to(device)
model.eval()



@app.get("/")
def upload_image(request: Request):
    print(request)
    return templates.TemplateResponse("upload_image.html", context={'request': request, })


@app.post("/home")
def homepage(request: Request):

    global img_path, response, card_info

    time.sleep(0.3)
    t = os.path.join(path, 'd.txt')
    f = open(t, 'r')
    data = f.readline()
    img_path = os.path.join('static/', data.split('\\')[-1])
    f.close()
    os.remove(t)

    print(img_path)

    # rule-base
    response, result = grouping.main(img_path)
    r = rule.mainfun(result)
    rule_base_result = r[2:]


    #kobert
    card_info = kobert.run(model, tokenizer, device, img_path)
    kobert_result = [card_info['PER']['text'], get_mail(card_info['MAIL']['text']), get_only_num(card_info['TEL']['text']),
                     get_only_num(card_info['NUM']['text']), card_info['POS']['text'], card_info['PER_E']['text']]

    return templates.TemplateResponse("main.html", context={'request': request,
                                                            'image': img_path,
                                                            'rulebase': rule_base_result,
                                                            'kobert': kobert_result})

