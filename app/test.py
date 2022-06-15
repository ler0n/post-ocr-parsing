import os, json
import requests

import numpy as np

from PIL import Image

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import plotly.express as px
import plotly.graph_objects as go

# api 호출 이미지 폴더
IMG_PATH = 'static/fake_0002.jpg'
# key.json 파일 저장 폴더(API 호출 관련 기밀 정보 폴더)

import time

SECRET_PATH = ''

# api 사용하기
secret_file = os.path.join(SECRET_PATH, 'key.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

api_url = secrets['API_URL']
secret_key = secrets['SECRET_KEY']

headers = {"secret": secret_key}


file_dict = {"file": open(IMG_PATH, "rb")}
response = requests.post(api_url, headers=headers, files=file_dict)
result = response.json()

# 시각화 - 이미지도 열고, api 결과도 열어야 한다.


image = Image.open(IMG_PATH, 'r')

#api 결과 호출 -> result 사용
start = time.time()
fig = px.imshow(image, color_continuous_scale='gray')
for i, group in enumerate(result['ocr']['word']):
    pos = np.array(group['points']).transpose()
    fig.add_trace(go.Scatter(x=pos[0], y=pos[1], fill="toself", name=f"{group['text']}"))

fig.show()
# fig.write_image('test.png')
print("걸린시간: ", time.time() - start)
# fig.show()