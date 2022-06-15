import os, json
import requests
import pickle

from PIL import Image
import numpy as np

# api 호출 이미지 폴더
IMG_PATH = 'static/'
# key.json 파일 저장 폴더(API 호출 관련 기밀 정보 폴더)
SECRET_PATH = ''



def main(image_path):
    # API 정보 선언
    secret_file = os.path.join(SECRET_PATH, 'key.json')

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    api_url = secrets['API_URL']
    secret_key = secrets['SECRET_KEY']
    headers = {"secret": secret_key}

    file_dict = {"file": open(image_path, "rb")}
    response = requests.post(api_url, headers=headers, files=file_dict).json()
    group_list, corpus_list = serialization_by_rule(response)
    result = {'all': group_list, 'text_list': corpus_list}

    return response, result


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

        y_pos = np.mean(pos[1][[0, -1]])
        x_pos = np.mean(pos[0][[0, -1]])
        height = min(pos[1][-1] - pos[1][0], pos[1][-2] - pos[1][1])

        if ele['text'] == '/':
            pass
        elif len(group_list) != 0:
            for idx, group in enumerate(group_list):
                if group['text'] == '/': continue

                y_diff = abs(y_pos - np.mean(group['bound'][1][[0, -1]]))
                group_size = min(group['bound'][1][-1] - group['bound'][1][0],
                                 group['bound'][1][-2] - group['bound'][1][1])
                dis = abs(x_pos - np.mean(group['bound'][0][[1, 2]]))
                size_diff = abs(height - group_size)

                if (y_diff <= (group_size * 0.25) and \
                        size_diff <= (group_size * 0.25) and \
                        dis <= (group_size * 1.3)):
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