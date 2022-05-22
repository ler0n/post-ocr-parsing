from utils import *

'''
정보 생성 관련 내용은 메뉴얼 참고
'''

cnt = 1
print('시작하려면 엔터를 입력하세요')
while input()!='dd':
    print(f'[{cnt}개째 ... ("dd" 입력 시 종료)]')
    a,b,c,d,e = random_info()
    print('TEL:', a)
    print('핸드폰:', b)
    print('이메일:', c)
    print('이름:', d)
    print('직책:', e)
    cnt+=1

print('Done')