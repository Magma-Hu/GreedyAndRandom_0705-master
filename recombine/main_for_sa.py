# main函数调用
from after_blocks_allocation import *
import numpy as np
from before_blocks_allocation import *
from nodes_class import *
from blocks_class import *
import math
#from SA import SA
# if __name__ == '__main__':
def main_init(random_seed,nodeNum,blockNum,nodes_layout):
    # gml文件名，由节点数量和节点分布决定
    filename = 'D:/python-code/GreedyAndRandom_0705-master/Model/NodeInfo/run_count_0/20nodes_50blocks_origin_NodeInfo.gml'.format(nodeNum,nodes_layout)

    # 从gml文件中提取节点属性
    NodeNum, Node_capacity, Node_Tjk, Node_meanTj = extract_node_data_from_gml(filename,nodeNum)

    # 初始化节点
    nodes = NodeInit(NodeNum=NodeNum, Node_capacity=Node_capacity, Node_Tjk=Node_Tjk, Node_Tj=Node_meanTj, blockNum=blockNum)

    # 初始化区块
    blockNum, blockSize, blockTime = gen_block(blockNum=blockNum, seed=2)
    blocks = BlockInit(blockNum=blockNum, blockSize=blockSize, blockTime=blockTime, nodes=nodes)

    print('#<seed{random_seed}_{nodeNum}nodes_{Layout}_{blockNum}blocks>#'.format(
            random_seed = random_seed,nodeNum = len(nodes),Layout = nodes_layout,blockNum = len(blocks)))

    return nodes,blocks,Node_Tjk,Node_meanTj

# 初始化和实验分开，保证 nodes 和 blocks 不变
random_seed,nodeNum,blockNum,nodes_layout = (3,20,200,'origin')
nodes,blocks,Node_Tjk,Node_meanTj = main_init(random_seed,nodeNum,blockNum,nodes_layout)

def main_experiment(random_seed,nodes,blocks,nodes_layout,Node_Tjk,Node_meanTj) -> tuple[list[Block], list[Node], dict] :
    
    # 设置打印选项，显示完整的矩阵
    np.set_printoptions(threshold=np.inf)      

    Algorithm_list = [
        # '贪心算法',
        '两步式贪心算法',
        # '两步式贪心算法-KeepPv',
        # '两步式贪心算法-f*T/meanT',
        '两步式贪心算法-2018',
        'myTest',
        # '两步式贪心算法-FijAndPb',
        '随机算法']

    # 存储每个算法在当前区块和节点属性对应的区块分配方案
    block_node_alloDict = {}

    for Algorithm in Algorithm_list :
        block_node_alloDict[Algorithm] = Algorithm_Experiment(random_seed,nodes,blocks,Algorithm,nodes_layout,Node_Tjk,Node_meanTj)

    return blocks,nodes,block_node_alloDict

# 多种条件下的实验函数
# for random_seed in range(1,1001,200):
#     np.random.seed(random_seed)
#     for nodeNum in [10,20]:
#         for blockNum in range(50, 501, 50):     # 10nodes最多350
#             for nodes_layout in ['origin','randomLayout','springLayout']:
#                 main_experiment(random_seed,nodeNum,blockNum,nodes_layout)

blocks,nodes,block_node_alloDict = main_experiment(random_seed,nodes,blocks,nodes_layout,Node_Tjk,Node_meanTj)

########################################################################################################
#算出答案之后用遗传算法对分配结果进行进一步优化#
import random

# 适应度函数（将问题映射到适应度值）
# 计算区块分配方案的成本，成本越低的适应度越高
@calculate_time
def fitness_func(population,nodes,blocks):
    fitness_values = []
    for allo in population:
        if allo.size != 0:
            fitness_values.append(calculate_nodesCost(np.array(allo),nodes,blocks))#没看到这个函数定义啊，咋算的损失（）
    return np.array(fitness_values)

# 选择操作
@calculate_time
def selection(population, fitness_values, num_parents):

    # fitness_sort = np.argsort(fitness_values)
    # elite_offspring_indices  = fitness_sort[:3]
    # random_offspring_indices = fitness_sort[num_parents:num_parents+1]
    # parents_indices = np.concatenate((elite_offspring_indices,random_offspring_indices))
    #unique_values = list(set(fitness_values))#转化成列表
    unique_values = list(fitness_values)#转化成列表
    sorted_values = sorted(unique_values)#排序
    if len(sorted_values) >= num_parents: #如果排序后适应度值的长度不少于需要的父代数量
            indices = [list(fitness_values).index(value) for value in sorted_values]
            parents_indices = np.array(indices)[:num_parents]
            if len(sorted_values)>8:
                parents_indices_to_delete = indices[8:]
                population = np.delete(population, parents_indices_to_delete)
                print(len(population))
    else:
        raise Exception('种群中全是重复的元素')

    parents = np.array(population)[parents_indices]
    return parents,parents_indices,population


# 使得单个节点的存储空间满足约束
# @calculate_time
def constrain_node_space(node_index,blockSi,offspring_allo,nodes,blocks):

    # 取每列区块的备份数
    blocks_backup = np.array([np.sum(offspring_allo[:,i]) for i in range(len(blocks))])#offspring_allo每一列求和结果，共len(blocks)列
    blockIndex_0 = np.where(offspring_allo[node_index] == 0)[0]#这个[0]是什么意思，某节点第一个值为0的索引？
    blockIndex_1 = np.where(offspring_allo[node_index] == 1)[0]#返回的是元组中的数组
    blockSi_0 = [blockSi[index] for index,value in enumerate(offspring_allo[node_index]) if value == 0]#这一步的意义是？看看这个节点里面哪个区块是0的
    blockSi_0 = np.array(blockSi_0) 

    # 在当前的分配方案下区块存储所花费的总空间
    blocks_space = np.sum(offspring_allo[node_index,:]*blockSi)
    extra_space = nodes[node_index].capacity - blocks_space 

    # 当节点 j 的多余空间大于任意一个未分配区块的大小时：
    while(np.any(extra_space > blockSi_0) ) :

        # 随机选一列由 0 置为 1                
        block_index = np.random.choice(blockIndex_0)
        while(blockSi[block_index] > extra_space):
            block_index = np.random.choice(blockIndex_0)#干嘛，放不下就随机选一个？另一个也放不下咋办
        offspring_allo[node_index][block_index] = 1#懂，放个放得下的
        extra_space -=  blockSi[block_index]
        # print(f'节点{j}区块{block_index}由0置为1')
        # 选计算总成本最低的一列由 0 置为 1

    while(extra_space < 0) :#这还能小于0，咋不上天。好叭这种计算方式确实有可能小于0

        # 随机选一列由 1 置为 0                
        block_index = np.random.choice(blockIndex_1)#挑选数组中某个区块
        while(blocks_backup[block_index] < 2):#如果这个区块的备份数量在整个集群里为1或者0（但是不可能为0啊）
            block_index = np.random.choice(blockIndex_1)#那不得行要重新抽一个
        offspring_allo[node_index][block_index] = 0#腾出空间然后置为0。     我觉得要计算一下访问成本然后选个最低的
        extra_space =  extra_space + blockSi[block_index]#把存储资源加回来
        blockIndex_1 = np.where(offspring_allo[node_index] == 1)[0]#更新一下备份1的列表
        blocks_backup = np.array([np.sum(offspring_allo[:,i]) for i in range(len(blocks))])#更新一下存储备份

    pass

# 使得单个区块的备份数量满足约束
# @calculate_time
def constrain_block_backup(block_index,offspring_allo,nodes,blocks):

    block_backup = np.sum(offspring_allo[:,block_index])

    while block_backup < 2 :#如果备份数量小于2
        node_index = np.random.choice(list(range(len(nodes))))#随机挑选一个幸运节点
        offspring_allo[node_index][block_index] = 1#给他把区块变1 (==)？
        #剩余资源不改的吗？？？？？
    pass

#工具函数
def sigmoid(x):
    return 1 / (1 + np.exp(x))

def drop(t_now,now_generation):
    t_now=t_now/math.log(now_generation+2,10)
    #t_now=t_now/(now_generation+1)
    return t_now
# 画图
import matplotlib.pyplot as plt
def plot_best_fitness(best_fitness):
    """
    绘制最佳个体适应度值随迭代次数的变化曲线。

    参数：
    - best_fitness: 包含每一代最佳个体适应度值的列表。例如，[0.5, 0.4, 0.3, ...]

    """

    # 生成迭代次数列表
    generations = range(len(best_fitness))

    # 绘制曲线
    plt.rcParams['font.family'] = 'SimSun'
    plt.plot(generations, best_fitness)
    plt.xlabel('迭代次数')
    plt.ylabel('最佳个体适应度值')
    plt.title('最佳个体适应度值随迭代次数的变化')
    plt.grid(True)
    plt.show()


#算法函数
#import copy
def cross(allo1,allo2):
    # 按列（区块）交叉时
    #if np.array_equal(allo1,allo2):
    #    print('cross ???')
    allo_temp1=allo1.copy()
    allo_temp2=allo2.copy()
    allo_size=allo1.shape
    index1=random.randint(0,allo_size[1]-2)
    index2=random.randint(index1,allo_size[1]-2)
    allo1[:,index1:index2+1]=allo_temp2[:,index1:index2+1]
    allo2[:,index1:index2+1]=allo_temp1[:,index1:index2+1]
    #if np.array_equal(allo1,allo_temp1):
    #    print('cross 失败')
    return allo1,allo2  

def check_duplicate(population):
    unique_elements, counts = np.unique(population, return_counts=True)
    if len(unique_elements) == 1:
        print("All elements in the array are duplicates.")
        return False 
    else:
        print("There are unique elements in the array.")
        return True
    
def SA(population,threshold,nodes,blocks,temperature):
    population_temp=population.copy()
    #假设录入的分配方案数量和GA一样都是8个
    blockSi = np.array([block.Si for block in blocks])
    #values=fitness_func_0327(population,nodes,blocks)
    #print(values)
    #flag=check_duplicate(population)
    #随机选择多对父代进行交叉，产生领域解 
    # 随机打乱元素顺序
    np.random.shuffle(population)
    # 将元素两两配对
    #pairs = [(population[i], population[i+1]) for i in range(0, len(population), 2)]
    for i in range(len(population)//2):
        population[i],population[i+4]=cross(population[i],population[i+4])
    #values=fitness_func_0327(population,nodes,blocks)
    #print(values)
    #input()
    #print('交叉完毕')
    #判断新解是否仍然满足约束条件
    for _,population_ in enumerate(population):
    #for population_ in population:
        # 使得每一个区块满足备份约束
        for block_index in range(len(blocks)):
            constrain_block_backup(block_index,population_,nodes,blocks)
        # 使得每一个节点满足存储资源约束
        for node_index in range(len(nodes)):
            constrain_node_space(node_index,blockSi,population_,nodes,blocks)
    #values=fitness_func_0327(population,nodes,blocks)
    #print(values)
    #交叉后计算耗时，降低就接受解，不降低就以一定概率接受解
    cost_before_mean = np.mean(fitness_func_0327(population_temp,nodes,blocks))
    cost_after_mean = np.mean(fitness_func_0327(population,nodes,blocks))
    delta_cost=cost_before_mean-cost_after_mean
    print('cost_before_mean',cost_before_mean)
    print('cost_after_mean',cost_after_mean)
    print('delta_cost',delta_cost)
    if delta_cost>0 :#新解比较好
        print('接受新解')
        #input()
        return population,nodes,blocks,delta_cost
    #elif delta_cost<0 or random.random() > sigmoid(delta_cost / temperature):#不好，但是一定概率接受
    elif  random.random() > sigmoid(delta_cost / temperature):#不好，但是一定概率接受
        print('概率：',sigmoid(delta_cost / temperature))
        print('勉强接受新解')
        #input()
        return population,nodes,blocks,delta_cost
    else:#接受不了一点
        print('不接受新解')
        population=population_temp
        #input()
        return population,nodes,blocks,delta_cost

def algorithm3_sa(population,threshold,nodes,blocks,temperature):
    population,nodes,blocks,delta_cost=SA(population,threshold,nodes,blocks,temperature)
    return population,nodes,blocks,delta_cost
#保存和加载函数
import time
def save_user(now_generation,input_data,name):
    timestamp = int(time.time())
    savepath=f'D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/{name}/5_temperature_500_{name}_{now_generation}_{timestamp}.npy'#######
    np.save(savepath,input_data)

def load_user(loadpath,allow_pickle=True):
    return np.load(loadpath,allow_pickle=allow_pickle)


# 复制两种分配方案作为初始种群
#AlgorithmList = ['myTest','myTest','myTest','myTest','myTest','myTest','myTest','myTest']
#population = create_population(block_node_alloDict, AlgorithmList, population_size)
savepath1='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/population1/population1_999_1710605457.npy'
#savepath3='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/temperature_sa/4_temperature_500_temperature_sa_999_1711545444.npy'
savepath4='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/nodes/nodes_999_1710605457.npy'
savepath5='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/blocks/blocks_999_1710605457.npy'
population=load_user(savepath1)
#temperature=load_user(savepath3)
nodes=load_user(savepath4,allow_pickle=True)
blocks=load_user(savepath5)


# 遗传算法参数
population_size = 8  # 种群大小
num_generations = 500  # 迭代次数
temperature=100

fitness_values = fitness_func_0327(population,nodes,blocks)
#_,_,population=selection(population,fitness_values,2)



threshold=1e-4
best_fitness3=[]
best_fitness3_mean=[]
delta_costs=[]

for now_generation in range(num_generations):
    population,nodes,blocks,delta_cost=algorithm3_sa(population,threshold,nodes,blocks,temperature)
    temperature=drop(temperature,now_generation)
    delta_costs.append(delta_cost)
    fitness_value=fitness_func_0327(population,nodes,blocks)
    #print(fitness_value)
    best_fitness3_mean.append(np.mean(fitness_value))
    best_fitness3.append(min(fitness_value)) 
    if (now_generation+1)%10==0:############
        save_user(now_generation,population,'population_sa')
        save_user(now_generation,temperature,'temperature_sa')
        save_user(now_generation,nodes,'nodes_sa')
        save_user(now_generation,blocks,'blocks_sa')
plot_best_fitness(best_fitness3)
plot_best_fitness(best_fitness3_mean)
plot_best_fitness(delta_costs)
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness33_mean_3_main_for_sa_1.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness3_mean))
                    f.close()
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness3_main_for_sa_1.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness3))
                    f.close()
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/delta_costs_for_sa_1.0.txt', 'a') as f:
                    f.write('{0}\n'.format(delta_costs))
                    f.close()

