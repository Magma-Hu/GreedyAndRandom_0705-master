from after_blocks_allocation import *
import numpy as np
from before_blocks_allocation import *
from nodes_class import *
from blocks_class import *
import math
import random
from main_for_sa import constrain_node_space,constrain_block_backup,sigmoid
def cross(allo1,allo2):
    # 按列（区块）交叉时
    allo_size=allo1.shape
    index1=random.sample(range(allo_size[1]))
    index2=random.randint(index1,allo_size[1])
    allo1[:][index1:index2+1],allo2[:][index1:index2+1]=allo2[:][index1:index2+1],allo1[:][index1:index2+1]
    return allo1,allo2

def SA(population,threshold,nodes,blocks,temperature):
    population_temp=population
    #假设录入的分配方案数量和GA一样都是8个
    blockSi = [block.Si for block in blocks]
    blockSi = np.array(blockSi)
    #随机选择多对父代进行交叉，产生领域解
    for i in range(len(population)//2):
        population[i],population[i+len(population)//2]=cross(population[i],population[i+len(population)//2])
    #判断新解是否仍然满足约束条件
    # 使得每一个区块满足备份约束
    for block_index in range(len(blocks)):
        constrain_block_backup(block_index,population,nodes,blocks)
    # 使得每一个节点满足存储资源约束
    for node_index in range(len(nodes)):
        constrain_node_space(node_index,blockSi,population,nodes,blocks)
    #交叉后计算耗时，降低就接受解，不降低就以一定概率接受解
    cost_temp=0
    cost_current=0
    for allo in population_temp:
        cost_temp+=calculate_nodesCost(allo,nodes,blocks)
    for allo in population:
        cost_current+=calculate_nodesCost(allo,nodes,blocks)
    #达到阈值后停止或者迭代到一定轮次后停止
    delta_cost=cost_temp-cost_current
    if delta_cost>0 and delta_cost<threshold:
        return population,nodes,blocks
    elif delta_cost>0 and random.random() < sigmoid(delta_cost / temperature):
        return population,nodes,blocks
    else:
        population=population_temp
        return population,nodes,blocks
        