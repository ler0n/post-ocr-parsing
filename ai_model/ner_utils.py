import os
import json
import requests
import pickle

import torch

import numpy as np

from PIL import Image

from model import CardNERClassifier

from utils import get_label_name, load_tokenizer
from data import USE_NER_TAG, MODEL_PATH, SECRET_PATH

def get_model_tokenizier_device(model_path):
    with open(os.path.join(model_path, 'args.pickle'), 'rb') as f:
        args = pickle.load(f)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = CardNERClassifier.load_from_checkpoint(checkpoint_path=os.path.join(model_path, 'model.ckpt'),
                                                   args=args, device=device)
    tokenizer = load_tokenizer(MODEL_PATH)
    return model, tokenizer, device

def serialize_by_slope(response):
    response['ocr']['word'] = sorted(response['ocr']['word'], key=lambda x: x['points'][0][1])
    for i, ele in enumerate(response['ocr']['word']):
        if 'y_ind' in ele: continue
        ele['y_ind'] = ele['points'][-1][1]
        pos = np.array(ele['points']).transpose()
        x = ((pos[0][0] + pos[0][-1]) / 2, (pos[1][0] + pos[1][-1]) / 2)
        y = ((pos[0][1] + pos[0][-2]) / 2, (pos[1][1] + pos[1][-2]) / 2)
        slope = (y[1] - x[1]) / (y[0] - x[0])
        y_add = x[1] + (-x[0] * slope)
        for com in response['ocr']['word'][i+1:]:
            com_pos = np.array(com['points']).transpose()

            flag = False
            for i in range(np.min(com_pos[0]), np.max(com_pos[0])+1):
                y_pos = slope*i + y_add
                if 'y_ind' in com: continue
                if y_pos >= np.min(com_pos[1]) and y_pos <= np.max(com_pos[1]):
                    flag = True
                    com['y_ind'] = ele['points'][-1][1]
                    break
            
            if flag is False:
                break

    response['ocr']['word'] = sorted(response['ocr']['word'], key=lambda x: (x['y_ind'], x['points'][0][0]))

    line = [ele['text'] for ele in response['ocr']['word']]
    return line

def serialize(response, img_size):
    response['ocr']['word'] = sorted(response['ocr']['word'], key=lambda x: x['points'][-1][1])
    for i, ele in enumerate(response['ocr']['word']):
        if 'y_ind' in ele: continue
        ele['y_ind'] = ele['points'][-1][1]
        for com in response['ocr']['word'][i+1:]:
            if abs(ele['points'][-1][1] - com['points'][-1][1]) <= img_size[1]*0.01:
                com['y_ind'] = ele['points'][-1][1]
            else: break

    response['ocr']['word'] = sorted(response['ocr']['word'], key=lambda x: (x['y_ind'], x['points'][-1][0]))

    line = [ele['text'] for ele in response['ocr']['word']]
    return line

def get_card_info(group_config):
    group = { cls : {'text': '', 'rate': 0.0, 'bbox': []} for cls in USE_NER_TAG}

    for grp in group_config:
        if int(grp['rate'] / grp['num']) > int(group[grp['class']]['rate']) or \
           (int(grp['rate'] / grp['num']) == int(group[grp['class']]['rate']) and \
            len(grp['text']) > len(group[grp['class']]['text'])):
            group[grp['class']]['text'] = grp['text']
            group[grp['class']]['rate'] = grp['rate']/ grp['num']
            group[grp['class']]['bbox'] = grp['bbox']

    return group

def convert_line_to_tensor(line, tokenizer, device):
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token

    pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index

    tokens = []
    slot_label_mask = []
    for word in line:
        word_tokens = tokenizer.tokenize(word)
        if not word_tokens:
            word_tokens = [unk_token]
        tokens.extend(word_tokens)
        slot_label_mask.extend([0] + [pad_token_label_id] * (len(word_tokens) - 1))

    tokens += [sep_token]
    slot_label_mask += [pad_token_label_id]

    tokens = [cls_token] + tokens
    slot_label_mask = [pad_token_label_id] + slot_label_mask

    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    attention_mask = [1 if True else 0] * len(input_ids)

    input_ids = torch.tensor(input_ids, dtype=torch.long).unsqueeze(0)
    attention_mask = torch.tensor(attention_mask, dtype=torch.long).unsqueeze(0)

    input_ids = input_ids.to(device)
    attention_mask = attention_mask.to(device)

    return input_ids, attention_mask, slot_label_mask, pad_token_label_id

def get_prediction(model, tokenizer, device, response, img_size):
    line = serialize(response, img_size)
    input_ids, att_mask, slot_label_mask, pad_token_label_id = convert_line_to_tensor(line, tokenizer, device)

    outputs = model(input_ids, attention_mask=att_mask)
    logits = outputs[0].detach().cpu().numpy()
    preds = np.argmax(logits, axis=2)
    
    preds_list = []
    preds_rate = np.max(logits, axis=2)[0]

    for j in range(preds.shape[1]):
        if slot_label_mask[j] != pad_token_label_id:
            preds_list.append(get_label_name(preds[0][j]))

    entity_list = []
    text = ''
    for i, ele in enumerate(response['ocr']['word']):
        text += ' ' + ele['text'][:]
        split_list = preds_list[i].split('-')
        if len(split_list) != 2: continue
        cate, bio = split_list
        pred_rate = preds_rate[i]
        
        if bio == 'B':
            new_ent = {'class': cate, 'text': ele['text'][:], 'rate': pred_rate, 'bbox': ele['points'], 'num': 1}
            entity_list.append(new_ent)
        elif len(entity_list) != 0 and entity_list[-1]['class'] == cate:
            entity_list[-1]['text'] += ele['text'][:]
            entity_list[-1]['bbox'][1:3] = ele['points'][1:3]
            entity_list[-1]['rate'] += pred_rate
            entity_list[-1]['num'] += 1

    return entity_list

def get_secret_info():
    secret_file = os.path.join(SECRET_PATH, 'key.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())
    
    return secrets

def get_api_result(img_path):
    secrets = get_secret_info()

    api_url = secrets['API_URL']
    secret_key = secrets['SECRET_KEY']

    headers = {"secret": secret_key}
    file_dict = {"file": open(img_path, 'rb')}
    response = requests.post(api_url, headers=headers, files=file_dict).json()
    return response

def run_ner_model(img_path, model, tokenizer, device):
    img_size = Image.open(img_path).size
    response = get_api_result(img_path)
    group_info = get_prediction(model, tokenizer, device, response, img_size)
    card_info = get_card_info(group_info)
    return card_info