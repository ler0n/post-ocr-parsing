import csv

with open('0516.csv', 'w', newline='') as csvfile: #
    fieldnames = ['image_name', 'name', 'address', 'email', 'phone', 'role', 'OCR']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    # 만약 한줄 씩 추가하고 싶다 한다면
    # 위의 모드를 a 로 바꾸고 밑에 writer.writerheader 를 주석처리하고 돌리세용
    # 단, 첫 row 는 writer.writerheader 를 같이 돌리셔야 column 이 작성됩니다
    writer.writeheader()

    writer.writerow({'image_name': '1',
                      'name': '박지민',
                      'address': '서울시 강남구 역삼동 668-4번지, 4층',
                      'email': 'jumboprint@naver.com',
                      'phone': '02-555-6335',
                      'role': '대표이사',
                      'OCR': '',
                      })


    writer.writerow({'image_name': '2',
                     'name': '강엔젤',
                     'address': "엔젤시 엔젤구 엔젤로 1004, 엔젤빌딩 1004층",
                     'email': 'niacom2014@naver.com',
                     'phone': '010-0000-0000',
                     'role': '실장',
                     'OCR': '',
                     })

    writer.writerow({'image_name': '3',
                     'name': '송미라',
                     'address': '경기도 성남시 분당구 판교로 256번길 7',
                     'email': 'goodday@naver.com',
                     'phone': '010-5424-9876',
                     'role': '원장',
                     'OCR': '',
                     })

    writer.writerow({'image_name': '4',
                     'name': '김수지',
                     'address': 'A, 123-45, Street Name 231 Seoul, Korea',
                     'email': 'suji@soberano.com',
                     'phone': '02-123-4567',
                     'role': '대표',
                     'OCR': '',
                     })

    writer.writerow({'image_name': '5',
                     'name': 'KIM TAE HEE',
                     'address': "13, TAEBOKSAN-RO 3BEON-GIL, UICHANG-GU, CHANGWON-SI, GYEONGSANGNAM-DO, REPUBLIC OF KOREA",
                     'email': '',
                     'phone': '055-282-0321',
                     'role': 'GENERAL MANAGER',
                     'OCR': '',
                     })

    writer.writerow({'image_name': '6',
                     'name': '김보니',
                     'address': '서울 강남 논현로 123 1층',
                     'email': 'your_mail@naver.com',
                     'phone': '010-1234-5678',
                     'role': '대표',
                     'OCR': '',
                     })



# 틀
# writer.writerow({'image_name': '',
#                  'name': '',
#                  'address': '',
#                  'email': '',
#                  'phone': '',
#                  'role': '',
#                  'OCR': '',
#                  })