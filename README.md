# 최종 프로젝트 "너의 이름은"
## 프로젝트 소개
### 개요
Upstage의 기업 프로젝트로 데이터 사진으로부터 자동으로 필요한 정보를 추출하는 Post OCR Parsing 시스템을 AI 모델로 해결하는 프로젝트이다. 진행한 프로젝트는 명함 사진에서 이름, 전화번호, 직책, 이메일주소를 추출하는 모델 서비스를 제작하는 것이었다. 이를 위해 데이터 수집 과정부터 모델 성능 지표 설정 및 평가까지의 모든 과정을 정의하고 서비스를 구현하였다. 
### 데이터 수집 및 생성
#### 수집
구글 설문을 이용해 188개의 이미지를 수집했고, 7개를 제외하고 학습에 52개는 학습 과정에서 활용하고 129개는 모델 성능 평가에 활용했다.
#### 생성
필수정보(한글 이름, 직책과 소속), 부가정보(전화번호, 팩스번호, 핸드폰번호, 이메일, 주소), 그 외의 정보(회사명, 영어이름, 웹 주소, 로고, 구분자)를 랜덤으로 생성 후, 제작한 형식에 맞춰 명함 이미지를 생성했다. 명함 이미지에 사용한 정보들은 BIO Tag를 함께 생성하여 AI 모델 학습에 사용했다.
<img src="md_res/1.png" width="500">
### 모델
Rule 기반 모델과 AI 모델을 각각 제작해 두 모델의 성능을 평가하고, 각각의 장단점을 확인하였다.
<img src="md_res/2.png" width="500">
#### Rule 기반 모델
OCR API 결과에서 텍스트들을 grouping하는 과정을 거친 후, 각 텍스트의 카테고리를 분류하는 모델을 개발했다. 카테고리 사이의 간격이 짧다면 다른 카테고리의 단어가 묶인 경우에는 묶인 단어의 일부가 한 카테고리에 해당되면 다른 부분을 다시 Rule 기반 모델로 검사하는 반복 작업을 만들어 해결하였다.
#### AI(KoBERT) 기반 모델
OCR API로 추출한 텍스트들을 한 줄로 직렬화하고, 각 텍스트에 대해서 미리 정의한 카테고리로 분류하는 문제로 접근할 수 있다고 생각해 개체명 인식(NER; Named Entity Recognition)으로 해결하기 위해 모델을 설계했다. 개체명 인식 문제로 해결하는 방식 중 보편적인 BIO Tagging 방식을 채택했고, 분류 태그는 총 9개 태그로 구분하도록 했다.

<img src="md_res/3.png" width="200">

### 성능 평가 및 비교
평가 지표는 OCR API의 오류를 감안해 CER 기준 0.2 내의 오차는 수용하는 보정된 F1 score를 사용했다.

<img src="md_res/4.png" width="200">

### 서비스 시연
<img src="md_res/5.png" width="500">

## 팀 소개
| [ ![구창회](https://avatars.githubusercontent.com/u/63918561?v=4) ](https://github.com/sonyak-ku) | [ ![김지원](https://avatars.githubusercontent.com/u/97625330?v=4) ](https://github.com/Jiwon1729) | [ ![전민규](https://avatars.githubusercontent.com/u/85151359?v=4) ](https://github.com/alsrb0607) | [ ![정준우](https://avatars.githubusercontent.com/u/39089969?v=4) ](https://github.com/ler0n) |
|:-----------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------:|
|                              [ 구창회 ](https://github.com/sonyak-ku)                             |                              [ 김지원 ](https://github.com/Jiwon1729)                             |                              [ 전민규 ](https://github.com/alsrb0607)                             |                              [ 정준우 ](https://github.com/ler0n)                             |
|                              데이터 수집, 프론트엔드 개발                             |                     Rule 기반 모델 구현, 수집 데이터 labeling, 발표                    |                               PM, 데이터 생성 및 labeling, 발표                              |                                OCR output 직렬화, AI 모델 구현                                

## Repo 구조

```
ai_model # AI 모델 구현 관련 폴더
├─ dataset.py
├─ model.py
├─ main.py
├─ utils.py
└─ ner_utils.py
```
## 참고 자료
- [https://openreview.net/pdf?id=SJgjf695UB](https://openreview.net/pdf?id=SJgjf695UB)
- [https://github.com/monologg/HanBert-Transformers](https://github.com/monologg/HanBert-Transformers)
- [https://wikidocs.net/24682](https://wikidocs.net/24682)

