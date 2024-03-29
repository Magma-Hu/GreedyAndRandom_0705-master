#算法函数
import random
import copy
import numpy as np
def cross(allo1,allo2):
    # 按列（区块）交叉时
    #if np.array_equal(allo1,allo2):
    #    print('cross ???')
    allo_temp1=allo1.copy()
    allo_temp2=allo2.copy()
    allo_size=allo1.shape
    index1=random.randint(0,allo_size[1]-1)
    index2=random.randint(index1,allo_size[1]-1)
    allo1[:,index1:index2+1]=allo_temp2[:,index1:index2+1]
    allo2[:,index1:index2+1]=allo_temp1[:,index1:index2+1]
    #if np.array_equal(allo1,allo_temp1):
    #    print('cross 失败')
    return allo1,allo2  


allo1=np.array([[1,2,3,6,3],[1,2,3,6,3],[1,2,3,6,3]])
allo2=np.array([[1,2,4,9,0],[1,2,4,9,0],[1,2,4,9,0]])
allo1_n,allo2_n=cross(allo1,allo2)
print(allo1_n)
print(allo2_n)