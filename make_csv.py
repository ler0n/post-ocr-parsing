import csv
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2

image_dir = 'data/untracked/' # 이미지들 위치
csv_dir = '' # csv 파일 위치
print("csv 추가 -> a, 새로 csv 생성 -> w")
mode = input("mode: ")
csv_name = input("Name of the csv file: ")


with open(os.path.join(csv_dir, csv_name), mode, newline='', encoding='ISO-8859-1') as csvfile: #
    fieldnames = ['image_name', 'name', 'email', 'phone', 'position']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    if mode == 'w':
        writer.writeheader()

    files = os.listdir(image_dir)
    tracked_file = set()

    for file in files:
        print('current file: ', file)
        if input('wanna write data? 1 >> ') != '1':
            if input('wanna terminate? 1 >> ') == '1':
                break
            else:
                continue

        fname = os.path.join(image_dir, file)
        original = cv2.imread(fname, cv2.IMREAD_COLOR)
        cv2.imshow('Original', original)
        print('click the image and type "c" when you ready!')
        key = cv2.waitKey(0) & 0xFF # buffer

        img_name, name, email, num, pos = '', '', '', '', ''
        if key == ord('c'):
            while True:
                tracked_file.add(file)
                print('입력중..')
                img_name = input('사진이름: ')
                name = input('사람 이름: ')
                email = input('이메일: ')
                num = input("전화번호: ")
                pos = input('직책: ')

                print('\n')
                print("작성한 내용")
                print(f'사진이름: {img_name}\n사람 이름: {name}\n이메일: {email}\n전화번호: {num}\n직책: {pos}')

                if input("made mistake?" '1: ') != '1':
                    break

        writer.writerow({'image_name': img_name,
                          'name': name,
                          'email': email,
                          'phone': num,
                          'position': pos,
                          })

        cv2.destroyAllWindows()

    print(f'untracked files\n{set(files)-tracked_file}')

