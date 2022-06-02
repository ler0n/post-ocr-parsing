import pandas as pd
import math
import numpy as np
import pickle
# 인덱스를 지정해 시트 설정
df_sheet_index = pd.read_excel('img_R_excel.xlsx', engine='openpyxl')
aprime=[]
a=df_sheet_index.values.tolist()
# print(type(a[2][80]))
# a= a[np.logical_not(pd.isna(a))]
# a= pd.isna(a[1])
# print(a)

# for i in range(len(a)):
#     for j in range(len(a[i])):
#         print(type(a[i][j]))
#         if type(a[i][j])==type(a[2][80]):
#             print(1)
#             if np.isnan(a)==True:
#                 c=a[i][:j]
#                 aprime.append(a)
#                 break
# print(aprime)
# print(a)
b=[]
for i in range(len(a)):
    if i==0:
        temp=a[i]
        for i in range(len(temp)):
            if type(temp[i])==type(1.1):
                temp=temp[0:2]+(["  "])+temp[0:i]
                # print(temp)
                # np.isnan(temp[i]) == False
                break
        # temp = [x for x in temp if np.isnan(x) == False]
    else:
        if a[i][0]==a[i-1][0]:
            temp2=a[i]
            for i in range(len(temp2)):
                if type(temp2[i])==type(1.1):                                                                                
                    temp2=temp2[:i]
                    break
            temp=temp+(["  "])+temp2[2:]
            # temp.append(a[i])
            # temp = [x for x in temp if np.isnan(x) == False]
            b.append(temp)
        else:
            temp=a[i]
            for i in range(len(temp)):
                if type(temp[i])==type(1.1):
                    temp=temp[0:2]+(["  "])+temp[2:i]
                    # np.isnan(temp[i]) == False
                    break
    # print(temp)
# c=math.isnan(b)
# newlist = [x for x in b if np.isnan(x) == False]
print("------------")
print(b[16])
print("------------")
# for i in range(len(b[0])):
#     print(type(b[0][i]))
# print(len(b))
c=[]
for i in range(len(b)):
    temp=""
    for j in range(len(b[i])):
        temp+=str(b[i][j])+" "
    temp=temp[:-1]
    space_content = temp.replace(" "*4,"\t")
    c.append([temp])
# print(temp)
# print(c)
# c=" ".join(b[0])
# print(c)
# print("adfadsfadf")
print(type(c))
with open('sp500.txt','w',encoding='utf-8') as f:
    for name in c:
        for name2 in name:
            # print(type(name))
            # pickle.dump(name, f)
            f.write(name2)
        f.write('\n')
# with open('sp500.txt', 'rb') as lf:
#     readList = pickle.load(lf)
#     print(readList)