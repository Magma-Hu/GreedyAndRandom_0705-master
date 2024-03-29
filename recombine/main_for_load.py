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

# 创建初始种群
@calculate_time
def create_population(alloDict,alloDictKey,population_size):
    population = []
    for _ in range(population_size):
        population.append([])
    for index,key in enumerate(alloDictKey) :
        population[index] = np.array(alloDict[key])
    return population

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

# 交叉操作
@calculate_time
def crossover(parents, offspring_size):

    # 子代和父代的初始化
    offspring = np.zeros(offspring_size)#设置子代大小（offspring——size应该是一个1*3的数组）
    parents_index = list(range(len(parents)))#父代序号，有啥必要么

    # 为每个子代随机选择父代
    random.shuffle(parents_index)#随机打乱父代顺序
    for i in range(len(offspring)):
        offspring[i] = parents[parents_index[i % len(parents)]]#6，这随机吗

    # # 按行（节点）交叉时
    # nodes_index = list(range(offspring_size[1]))
    # nodes_length = len(nodes_index) // 2
    # for j in range(len(offspring)):
    #     nodes_index = random.sample(nodes_index, nodes_length)
    #     for i in nodes_index:
    #         offspring[j][i,:] = parents[-parents_index[j % len(parents)]+1][i,:]
       
    # 按列（区块）交叉时
    blocks_index = list(range(offspring_size[2]))#？？offspring_size不是个值吗？？，这句很奇怪没看懂。如果offspring是一个1*3的数组
    blocks_length = len(blocks_index) // 2
            
    for j in range(len(offspring)):
        blocks_index = random.sample(blocks_index, blocks_length)#随即在区块序数列表中抽取区块集合长度个序数
        for i in blocks_index:
            offspring[j][:,i] = parents[-parents_index[j % len(parents)]+1][:,i]#-parents_index[j % len(parents)有啥意义，不过这句的意思应该是把对应子代的列用父代的列替换掉。所有节点固定地方区块替换掉

    return offspring

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

# 变异 将不可行的解转为可行的解 同时满足节点和区块的约束
@calculate_time
def mutation(offspring,nodes,blocks,rate_generation):

    # 一维数组：存储所有区块的大小
    blockSi = [block.Si for block in blocks]
    blockSi = np.array(blockSi)

    # 循环每一个子代
    for index,offspring_allo in enumerate(offspring):

        # 只变异矩阵中某一个点，只将0变为1，向成本最低的情况变异？
        # 不会导致区块备份出现问题，按节点交叉时还是会导致节点空间不足
        for _ in range(1):
            j = random.sample(list(range(len(nodes))), 1)[0]#随机挑选一个幸运node
            block_index = random.sample(list(range(len(blocks))), 1)[0]#随机挑选一个幸运区块
            offspring_allo[j][block_index] = 1#把这个幸运节点的幸运区块置1

        # 使得每一个区块满足备份约束
        for block_index in range(len(blocks)):
            constrain_block_backup(block_index,offspring_allo,nodes,blocks)

        # 使得每一个节点满足存储资源约束
        for node_index in range(len(nodes)):
            constrain_node_space(node_index,blockSi,offspring_allo,nodes,blocks)

    return offspring
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
def algorithm1(parents1,offspring1,temperature,population1):
    '''cost_parent_mean=0
    for j in parents1:
        cost_parent_mean+=calculate_nodesCost(j,nodes,blocks)
    cost_parent_mean=cost_parent_mean/(len(parents1)) 
    cost_offspring_mean=0
    for i in offspring1:
        cost_temp=calculate_nodesCost(i,nodes,blocks)
        cost_offspring_mean+=cost_temp
    cost_offspring_mean=cost_offspring_mean/(len(offspring1))'''

    cost_parent_mean = np.mean(fitness_func_0327(parents1,nodes,blocks))
    cost_offspring_mean = np.mean(fitness_func_0327(offspring1,nodes,blocks))

    delta_cost=cost_parent_mean-cost_offspring_mean
    population_temp=population1[:]
    if delta_cost > 0 or random.random() < sigmoid(delta_cost / temperature):#随着轮次增加变得更容易接受新解？temp变小，delta变大，这合理吗，应该设置成大于。
        #print('接受新解')
        population1[:num_parents] = parents1
        population1[num_parents:] = offspring1 #直接用生成的子代替代了父代后面6个= =,感觉可以优化？？毕竟这样效率比较低，又不能保证子代比父代强
    else:
        population1=population_temp
        #print('不接受')
    return population1

def algorithm2(parents2,offspring2,population2):
    population2[:num_parents] = parents2
    population2[num_parents:] = offspring2
    return population2
     
'''def algorithm3_sa(T,population,threshold,nodes,blocks,temperature):
    for _ in range(T):
        population,threshold,nodes,blocks=SA(population,threshold,nodes,blocks,temperature)
        temperature=drop(temperature)'''

#保存和加载函数
import time
def save_user(now_generation,input_data,name):
    timestamp = int(time.time())
    savepath=f'D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/{name}/6_temperature_500_{name}_{now_generation}_{timestamp}.npy'
    np.save(savepath,input_data)

def load_user(loadpath,allow_pickle=True):
    return np.load(loadpath,allow_pickle=allow_pickle)


# 复制两种分配方案作为初始种群
#AlgorithmList = ['myTest','myTest','myTest','myTest','myTest','myTest','myTest','myTest']
#population = create_population(block_node_alloDict, AlgorithmList, population_size)
savepath1='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/population1/5_temperature_500_population1_9999_1710674970.npy'
savepath2='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/population2/5_temperature_500_population2_9999_1710674970.npy'
savepath3='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/temperature/5_temperature_500_temperature_9999_1710674970.npy'
savepath4='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/nodes/5_temperature_500_nodes_9999_1710674970.npy'
savepath5='D:/python-code/GreedyAndRandom_0705-master/recombine/model_save/blocks/5_temperature_500_blocks_9999_1710674970.npy'
population1=load_user(savepath1)
population2=load_user(savepath2)
temperature=load_user(savepath3)
nodes=load_user(savepath4,allow_pickle=True)
blocks=load_user(savepath5)


# 遗传算法参数
population_size = 8  # 种群大小
num_parents = 2  # 父代数量
#num_offspring=2
num_offspring = population_size - num_parents  # 子代数量，是必须要这么设置吗
num_generations = 10000  # 迭代次数
solution_size = (len(nodes),len(blocks)) # 解的大小:（行数:NodeNum，列数：BlockNum）
#initial_temperature=100#???
best_fitness2 = []
best_fitness1 = []
best_fitness1_mean=[]
best_fitness2_mean=[]
#temperature=initial_temperature

# 初始化父代
fitness_values1 = fitness_func(population1,nodes,blocks)
fitness_values2 = fitness_func(population2,nodes,blocks)
parents_indices1 = np.array(list(range(num_parents)))
parents_indices2 = np.array(list(range(num_parents)))
#初始父代相同
parents1 = population1[:num_parents] 
parents2 = population2[:num_parents] 

for now_generation in range(num_generations):

    #print(fitness_values[parents_indices])

# 初始化交叉 
    offspring1 = crossover(parents1, (num_offspring,) + solution_size)
    offspring2 = crossover(parents2, (num_offspring,) + solution_size)

# 初始化变异 
    offspring1 = mutation(offspring1,nodes,blocks,num_generations/2)
    offspring2 = mutation(offspring2,nodes,blocks,num_generations/2)


#模拟退火（判断是否可以接受新解，需要计算获得的子代的访问成本）
    #cost_parent=calculate_nodesCost(block_node_alloDict['myTest'],nodes,blocks)#这个地方不是很合理，父代会变化，计算的应该一直是父代，不是初代
    population1=algorithm1(parents1,offspring1,temperature,population1)
    population2=algorithm2(parents2,offspring2,population2)
    
# 初始化选择
    fitness_values1 = fitness_func(population1,nodes,blocks)
    fitness_values2 = fitness_func(population2,nodes,blocks)

    parents1,parents_indices1,population1 = selection(population1, fitness_values1, num_parents)
    parents2,parents_indices2,population2 = selection(population2, fitness_values2, num_parents)
  
    

    best_fitness1_mean.append(np.mean(fitness_values1))
    best_fitness2_mean.append(np.mean(fitness_values2))
    best_fitness1.append(fitness_values1[0])
    best_fitness2.append(fitness_values2[0])
    #print(f'迭代次数：{now_generation}，父代：',fitness_values1[parents_indices])
    
    temperature=drop(temperature,now_generation)

    if (now_generation+1)%1000==0:
        save_user(now_generation,population1,'population1')
        save_user(now_generation,population2,'population2')
        save_user(now_generation,temperature,'temperature')
        save_user(now_generation,nodes,'nodes')
        save_user(now_generation,blocks,'blocks')
#plot_best_fitness(best_fitness1)
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness11_mean_1_main3_4.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness1_mean))
                    f.close()
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness1_main3_4.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness1))
                    f.close()
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness22_mean_2_main3_4.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness2_mean))
                    f.close()
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness2_main3_4.0.txt', 'a') as f:
                    f.write('{0}\n'.format(best_fitness2))
                    f.close()

