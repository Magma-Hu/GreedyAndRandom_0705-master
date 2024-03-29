# 区块分配后的各项结果计算
import numpy as np
from before_blocks_allocation import *
from nodes_class import *
from blocks_class import *
# 区块分配后，计算节点 j 访问区块 i 的最小通信时延 Tji
def calculate_nodeTji(block_node_allo, node):
    # 计算Tji的方法：
    # 遍历分配方案 block_node_allo np的二维矩阵的每一列，索引为i
    # 取出每一列中不为 0 的行索引
    # 求出这些索引对应的最小的 nodes[j].Tjk[k]
    # 将其赋给 nodes[j].Tji[i]

    min_Tjk = []
    # 遍历每一列
    for i in range(block_node_allo.shape[1]):

        # 取出不为 0 的节点索引
        
        # non_zero_index = [row_index for row_index, value in enumerate(
        #     block_node_allo[:, i]) if value != 0]
        non_zero_index = np.flatnonzero(block_node_allo[:, i])

        # 对于每个节点，计算最小的 node.Tjk[k] 并赋给 node.Tji[i]
        min_Tjk.append(min([node.Tjk[k] for k in non_zero_index]))

    return np.array(min_Tjk)


# 区块分配后，计算所有节点的 Tji   
def calculate_Allnodes_Tji(block_node_allo,nodes):

    # 计算所有节点的 Tji
    for node in nodes:
        node.Tji = calculate_nodeTji(block_node_allo,node)#每个节点都遍历一遍，存进去的是元组
    

# 计算单节点成本
def calculate_nodeCost(node,blocks):

    # 计算单节点访问所有区块所需的加权成本:

    cost_j = sum(block.Wij[node.index] * node.Tji[block.index] for block in blocks) #

    return cost_j

# 计算总加权成本
def calculate_nodesCost(block_node_allo,nodes,blocks):

    # 计算所有节点的 Tji ,有查询成本后才能计算总的加权成本
    calculate_Allnodes_Tji(block_node_allo,nodes)

    cost_all = 0
    for node in nodes:
       cost_all += calculate_nodeCost(node,blocks)
    
    return cost_all

# 计算区块分配后区块占用的总空间
def calculate_block_space(blocks,block_node_allo):

    Block_space_sum = 0
    allo_column_sum = np.sum(block_node_allo, axis=0)
    for block in blocks:
        Block_space_sum += allo_column_sum[block.index] * block.Si

    return Block_space_sum

# 计算节点总容量和区块总大小
def calculate_CapacityAndSize(nodes,blocks):
    
    Node_capacity_sum = 0
    Block_size_sum = 0
    for node in nodes:
        Node_capacity_sum += node.capacity
    for block in blocks:
        Block_size_sum += block.Si

    return Node_capacity_sum,Block_size_sum 

# 打印所有节点的属性值
def print_NodesOrBlocks(nodes = None,blocks = None):

    if nodes :
        [nodes[_].print_attributes() for _ in range(len(nodes))]

    if blocks:
        [blocks[_].print_attributes() for _ in range(len(blocks))]

# 打印算法各项结果
def print_AlgoResult(nodes,blocks,Algorithm,random_seed,nodes_layout,cost_all = -1,block_node_allo = np.array([]),print_allo = False,save2file = True):

    import datetime,sys,os
    # 结果保存的日期
    current_date = datetime.date.today()
    month_day = current_date.strftime("%m-%d")

    # 文件夹路径与文件名
    folder_path = './Result/{date}'.format(date = month_day)
    os.makedirs(folder_path, exist_ok=True)
    filename = folder_path + '/seed{random_seed}_{nodeNum}nodes_{Layout}_{blockNum}blocks.txt'.format(
        random_seed = random_seed,nodeNum = len(nodes),Layout = nodes_layout,blockNum = len(blocks)
    )
    print_log = open(filename,"a")

    if save2file :
        savedStdout = sys.stdout  #保存标准输出流，不保存无法恢复默认值
        sys.stdout = print_log

    print('\n{0} 总加权成本：<{1}>'.format(Algorithm,cost_all))

    Node_capacity_sum,Block_size_sum = calculate_CapacityAndSize(nodes,blocks)
    print('节点总容量：{0} 区块总大小：{1}'.format(Node_capacity_sum,Block_size_sum))

    if block_node_allo.any() :
        Block_space_sum = calculate_block_space(blocks,block_node_allo)
        print('{0} 区块总占用空间：{1}'.format(Algorithm,Block_space_sum))

        allo_column_sum = np.sum(block_node_allo, axis=0)
        allo_row_sum = np.sum(block_node_allo, axis=1)
        print('{0} 各区块备份数量：\n{1}'.format(Algorithm,allo_column_sum))
        print('{0} 各节点存储数量：\n{1}'.format(Algorithm,allo_row_sum))

        if print_allo :
            print('{0} 区块分配方案：\n{1}'.format(Algorithm,block_node_allo))
    
    print('结果保存时间：'+str(datetime.datetime.now().time())+'\n')

    if save2file :
        sys.stdout = savedStdout
        print_log.close()
    

# 保存结果到文件
def save_AlgoResult(random_seed,nodes,nodes_layout,blocks,Algorithm,cost_all = -1,block_node_allo = np.array([])):
    
    import datetime,os
    # 结果保存的日期
    current_date = datetime.date.today()
    month_day = current_date.strftime("%m-%d")

    # 文件夹路径与文件名
    folder_path = './Result/{date}'.format(date = month_day)
    os.makedirs(folder_path, exist_ok=True)
    filename = folder_path + '/seed{random_seed}_{nodeNum}nodes_{Layout}_{blockNum}blocks.txt'.format(
        random_seed = random_seed,nodeNum = len(nodes),Layout = nodes_layout,blockNum = len(blocks)
    )

    with open(filename,'a') as file:
        file.write('\n{0} 总加权成本：<{1}>\n'.format(Algorithm,cost_all))

        Node_capacity_sum,Block_size_sum = calculate_CapacityAndSize(nodes,blocks)
        file.write('节点总容量：{0} 区块总大小：{1}\n'.format(Node_capacity_sum,Block_size_sum))

        if block_node_allo.any() :
            Block_space_sum = calculate_block_space(blocks,block_node_allo)
            file.write('{0} 区块总占用空间：{1}\n'.format(Algorithm,Block_space_sum))

            allo_column_sum = np.sum(block_node_allo, axis=0)
            allo_row_sum = np.sum(block_node_allo, axis=1)
            file.write('{0} 各区块备份数量：\n{1}\n'.format(Algorithm,allo_column_sum))
            file.write('{0} 各节点存储数量：\n{1}\n'.format(Algorithm,allo_row_sum))

            if False :
                print('{0} 区块分配方案：\n{1}\n'.format(Algorithm,block_node_allo))

        file.write('结果保存时间：'+str(datetime.datetime.now().time())+'\n')

# 算法实验函数
@calculate_time
def Algorithm_Experiment(random_seed,nodes,blocks,Algorithm,nodes_layout,Node_Tjk,Node_meanTj):

    if Algorithm == '贪心算法':
        # 贪心算法的区块分配方案
        block_node_allo = greedy_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法':
        # 贪心算法的区块分配方案
        block_node_allo = twoStepsGreedy_block_allocation(blocks,nodes)

    if Algorithm == '随机算法':
        # 随机算法的区块分配方案
        block_node_allo = random_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法-2018':
        # 两步式贪心算法-2018的区块分配方案
        block_node_allo = twoStepsGreedy2018_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法-FijAndPv':
        # 两步式贪心算法-FijAndPb的区块分配方案
        block_node_allo = twoStepsGreedyFijAndPv_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法-FijAndPb':
        # 两步式贪心算法-FijAndPb的区块分配方案
        block_node_allo = twoStepsGreedyFijAndPb_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法-KeepPv':
        # 贪心算法-KeepPv的区块分配方案
        block_node_allo = greedyKeepPv_block_allocation(blocks,nodes)

    if Algorithm == '两步式贪心算法-f*T/meanT':
        # 两步式贪心-f*T/meanT的区块分配方案
        block_node_allo = greedyfTmeanT_block_allocation(blocks,nodes)

    if Algorithm == 'myTest':
        block_node_allo = myTest_block_allocation_0811(blocks, nodes, Node_Tjk, Node_meanTj)

    # 计算算法所有节点的总加权成本
    cost_all = calculate_nodesCost(block_node_allo,nodes,blocks)
    # print('{}的分配方案:'.format(Algorithm)+'\n'+str(block_node_allo))

    # 打印算法结果
    print_AlgoResult(nodes,blocks,Algorithm,random_seed,nodes_layout,cost_all,block_node_allo)

    return block_node_allo


# 适应度函数,删去重复计算优化版本
def fitness_func_0322(population,nodes:list[Node],blocks):
    
    def calculate_refer_Tji(block_node_allo):

        Node_Tji = [calculate_nodeTji(block_node_allo,node) for node in nodes]
        ZeroInTji = [np.flatnonzero(block_node_allo[:, i]) for i in range(len(blocks))]

        return np.array(Node_Tji),np.array(ZeroInTji)

    def calculate_real_Tji(block_node_allo,refer_Node_Tji:np.ndarray,ZeroInReferTji):
        # i = 0
        Node_Tji = refer_Node_Tji.copy()
        for block_index in range(len(blocks)):
            non_zero_index = np.flatnonzero(block_node_allo[:, block_index])
            if np.array_equal(non_zero_index,ZeroInReferTji[block_index]):
                continue
            else:
                for node_index in range(len(nodes)):
                    Node_Tji[node_index][block_index] = min([nodes[node_index].Tjk[k] for k in non_zero_index])
        # print(f"避免重复计算{i}次")  
        return Node_Tji

    # 一维数组：存储每个分配方案的成本
    cost_values = []

    # 二维数组，存储某个种群节点访问区块的Tji值
    refer_Node_Tji,ZeroInReferTji = calculate_refer_Tji(population[0])
    
    # 将Wij转换为numpy数组，理论上只用转换一次，不用放入适应度的计算中
    Block_Wij = np.array([block.Wij for block in blocks]).T  # 转换为与nodes大小匹配的二维数组

    # 计算每个分配方案的成本表示适应值
    for allo in population:
        Node_Tji = calculate_real_Tji(allo,refer_Node_Tji,ZeroInReferTji)
        cost_values.append(np.sum(Block_Wij * Node_Tji))

    return np.array(cost_values)

import functools
# 适应度函数,使用缓存器版本
def fitness_func_0327(population,nodes:list[Node],blocks):

    @functools.lru_cache(maxsize = None)
    def min_Tji(non_zero_index):

        return  Node_Tjk[:, non_zero_index].min(axis = 1)

    @functools.lru_cache(maxsize = None)
    def nonzero_allo(allo_column):

        return  tuple(np.flatnonzero(np.array(allo_column)))

    def calculate_real_Tji(block_node_allo,Node_Tjk:np.ndarray):

        Node_Tji = np.zeros((len(nodes),len(blocks)))
        for block_index in range(len(blocks)):
            non_zero_index = nonzero_allo(tuple(block_node_allo[:, block_index]))
            Node_Tji[:, block_index] = min_Tji(non_zero_index)

        return Node_Tji

    # 一维数组：存储每个分配方案的成本
    cost_values = []
   
    # 将Wij转换为numpy数组，理论上只用转换一次，不用放入适应度的计算中
    Block_Wij = np.array([block.Wij for block in blocks]).T  # 转换为与nodes大小匹配的二维数组
    Node_Tjk = np.array([node.Tjk for node in nodes])        # 转换为与nodes大小匹配的二维数组

    # 计算每个分配方案的成本表示适应值
    for allo in population:
        Node_Tji = calculate_real_Tji(allo,Node_Tjk)
        cost_values.append(np.sum(Block_Wij * Node_Tji))

    return np.array(cost_values)