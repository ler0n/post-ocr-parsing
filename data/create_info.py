from utils import *

'''
정보 생성 관련 내용은 메뉴얼 참고
'''

cnt = 1
print('시작하려면 엔터를 입력하세요')
while input()!='dd':
    print(f'[{cnt}개째 ... ("dd" 입력 시 종료)]')
    random_info()
    cnt+=1

print('Done')