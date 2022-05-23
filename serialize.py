import os, json
import requests
import pickle

from PIL import Image
import numpy as np

# api 호출 이미지 폴더
IMG_PATH = 'img'
# key.json 파일 저장 폴더(API 호출 관련 기밀 정보 폴더)
SECRET_PATH = '.secret'
# api 호풀 후 결과 저장 폴더
RES_PATH = 'res'
# resize할 이미지 가로길이
WIDTH = 480


def main():
    # API 정보 선언
    secret_file = os.path.join(SECRET_PATH, 'key.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    if not os.path.isdir(RES_PATH): os.mkdir(RES_PATH)
    if not os.path.isdir(f'{IMG_PATH}/resize'): os.mkdir(f'{IMG_PATH}/resize')

    api_url = secrets['API_URL']
    secret_key = secrets['SECRET_KEY']

    headers = {"secret": secret_key}
    file_list = os.listdir(IMG_PATH)
    file_list_img = [file for file in file_list if file.split('.')[-1] in ['jpg', 'png', 'jpeg']]

    for file_img in file_list_img:
        img_path = image_preproces(file_img, WIDTH)
        file_dict = {"file": open(img_path, "rb")}
        response = requests.post(api_url, headers=headers, files=file_dict).json()
        group_list, corpus_list = serialization_by_rule(response)
        result = {'all': group_list, 'text_list': corpus_list}
        with open(os.path.join(RES_PATH, f'{file_img}_res.pickle'), 'wb') as outfile:
            pickle.dump(result, outfile)

def image_preproces(img_name, width):
    image = Image.open(os.path.join(IMG_PATH, img_name))
    wid, hei = image.size
    ratio = hei / wid
    image = image.resize((width, int(width * ratio)))
    save_path = os.path.join(IMG_PATH, f'resize/{img_name}') 
    image.save(save_path)
    return save_path

def serialization_by_rule(ocr_words):
    '''
    "points":[좌측 상단, 우측 상단, 우측 하단, 좌측 하단]
    "orientation":"Horizontal/Vertical",
    "text":"텍스트 내용"
    '''
    word_list = sorted(ocr_words['ocr']['word'], key=lambda x: x['points'][0])
    group_list = []
    corpus_list = []

    for ele in word_list:
        pos = np.array(ele['points']).transpose()

        y_pos = np.mean(pos[1])
        x_pos = np.mean(pos[0][[0, -1]])

        if ele['text'] in ['I', '|', '/']: pass
        elif len(group_list) != 0:
            for idx, group in enumerate(group_list):
                if group['text'] in ['I', '|', '/']: continue

                y_diff = abs(y_pos - np.mean(group['bound'][1]))
                group_size = ((group['bound'][1][-1] - group['bound'][1][0]) + \
                              (group['bound'][1][-2] - group['bound'][1][1])) / 2
                dis = abs(x_pos - np.mean(group['bound'][0][[1, 2]]))

                if (y_diff <= 5 and \
                    dis <= (group_size*1.2)):
                    group_list[idx]['bound'][:, 1:3] = pos[:, 1:3]
                    group_list[idx]['text'] += ele['text']
                    corpus_list[idx] += ele['text']
                    ele = None
                    break
        
        if ele is not None:
            group = {'bound': pos, 'text': ele['text']}
            group_list.append(group)
            corpus_list.append(ele['text'][:])

    return group_list, corpus_list

if __name__ == '__main__':
    main()