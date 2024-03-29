# 区块分配前的计算函数
from blocks_class import *
from nodes_class import *
# 计算全部区块和节点的能力
def calculate_capabilities(blocks, nodes):
    for block in blocks:
        block.Pb = calculate_block_capability(block=block)
    for node in nodes:
        node.Pv = calculate_node_capability(node=node)

# 计算区块 i 的重要性
def calculate_block_capability(block):

    # 计算区块重要性的方法:
    # Pb[i] = sum<j>(Block[i].Wij[j]) /(Block[i].Delta_i+1)
    return np.sum(block.Wij)/(block.Delta_i)

# 计算节点 j 的能力
def calculate_node_capability(node):

    # 计算节点能力的方法:
    # Pv[j] =  node.Sr/node.meanTj
    return 1/node.meanTjk
    return node.Sr/node.meanTjk

# 更新单个区块和节点能力
def update_capabilities(block, node):

    # 根据具体需求更新区块和节点的能力
    block.Pb = calculate_block_capability(block=block)
    node.Pv = calculate_node_capability(node=node)

# 更新分配结果
def assign_block_to_node(block, node, block_node_assign):
    index_block = block.index
    index_node = node.index
    if node.Sr > block.Si:
        block_node_assign[index_node][index_block] += 1
        node.Sr -= block.Si
        block.Delta_i += 1
    else :
        # print("节点 {0.index} 的存储空间 {0.Sr} 不足以存储区块 {1.index} 的大小 {1.Si}".format(node,block))  
        # raise Exception("结束")  
        pass
###################################################################################################################
# 贪心算法得出分配结果
def greedy_block_allocation(blocks:list[Block], nodes):

    block_node_allo: list[list[int]] = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    for block in blocks:
        block.Delta_i = 0    

    # 计算所有节点和区块的能力
    calculate_capabilities(blocks, nodes)
    
    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):

        # 选择满足约束的节点和区块
        selected_block,selected_node = choose_blockAndNode_greedy(blocks,nodes,block_node_allo)

        # 没有满足条件的区块则退出循环
        if selected_block == None and selected_node == None:
            break
        
        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)
        
        # 更新单个区块和节点的能力
        update_capabilities(selected_block, selected_node)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo

# 递归选择满足约束的节点和区块
def choose_blockAndNode_greedy(blocks:list[Block],nodes:list[Node],block_node_allo):

    # 选择具有最高 Pb 的区块
    if blocks != []:
        selected_block: Block = max(blocks, key=lambda block: block.Pb)
    
    # 所有的区块均不满足约束条件，则返回None
    else:
        return None,None

    # 仅保留 node.Sr 大于当前区块 block.Si 的节点，并且区块未曾被分配到此节点
    filter_nodes = filter(lambda node: node.Sr >= selected_block.Si and block_node_allo[node.index][selected_block.index] == 0,nodes)
    
    # 有满足约束的节点则输出
    if filter_nodes != []:

        # 选择具有最高 Pv 的节点，
        selected_node:Node = max(filter_nodes, key=lambda node: node.Pv)
        return selected_block,selected_node
    
    # 无则过滤掉此区块，递归选择剩下的区块，直到选出满足的区块和节点
    else:
        filter_blocks = filter(lambda block: block.index != selected_block.index,blocks)
        return choose_blockAndNode_greedy(filter_blocks,nodes,block_node_allo)

#################################################################################################################################
# 贪心算法-KeepPv得出分配结果
def greedyKeepPv_block_allocation(blocks, nodes):

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    for block in blocks:
        block.Delta_i = 0    

    # 计算节点和区块的能力
    calculate_capabilities(blocks, nodes)
    
    # 贪心算法-2018第一步
    while any(block.Delta_i == 0 for block in blocks):

        # 选择具有最高 Pb 的区块
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Pb)      

        # 选择具有最高 Pv 的节点，仅保留 node.Sr 大于当前区块 block.Si 的节点
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)

    # 计算节点和区块的能力
    calculate_capabilities(blocks, nodes)

    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):
        
        # 选择具有最高 Pb 的区块
        selected_block = max(blocks, key=lambda block: block.Pb)
        
        # 选择具有最高 Pv 的节点，仅保留 node.Sr 大于当前区块 block.Si 的节点
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)
        
        # 根据具体需求更新区块和节点的能力
        selected_block.Pb = calculate_block_capability(selected_block)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
######################################################################################################################################
# 两步式贪心算法得出分配结果
def twoStepsGreedy_block_allocation(blocks, nodes):

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    for block in blocks:
        block.Delta_i = 0    

    # 计算所有节点和区块的能力
    calculate_capabilities(blocks, nodes)
    
    # 第一步
    while any(block.Delta_i == 0 for block in blocks):

        # 选择具有最高 Pb 的区块，目标区块：未被备份的区块
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Pb)      

        # 选择具有最高 Pv 的节点，目标节点：node.Sr 大于当前区块 block.Si 的节点
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)
        
        # # 更新单个区块和节点的能力
        # update_capabilities(selected_block, selected_node)

    # 计算所有节点和区块的能力
    calculate_capabilities(blocks, nodes)

    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):
        # 选择具有最高 Pb 的区块
        selected_block = max(blocks, key=lambda block: block.Pb)
        
        # 选择具有最高 Pv 的节点，仅保留 node.Sr 大于当前区块 block.Si 的节点
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)
        
        # 更新单个区块和节点的能力
        update_capabilities(selected_block, selected_node)
        # selected_block.Pb = calculate_block_capability(selected_block)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
##############################################################################################################################
def random_block_allocation(blocks, nodes):

    import random

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点和区块有关区块分配的属性
    for node in nodes:
        node.Sr = node.capacity 
    for block in blocks:
        block.Delta_i = 0

    # 让每个区块均备份一次，确保最低备份数量的同时，防止计算 Tji（节点访问某区块的成本） 时报错
    for selected_block in blocks:
        cond_nodes = filter(lambda node: node.Sr >= selected_block.Si, nodes)

        # 随机选择节点
        selected_node = random.choice(list(cond_nodes))

        # 将区块分配给节点
        assign_block_to_node(selected_block, selected_node, block_node_allo)

    # print(np.sum(np.array(block_node_allo),axis=0))

    # # 只要有一个节点能够存放最大的区块，就进行循环
    # while any(node.Sr >= max(block.Si for block in blocks) and not np.all(np.array(block_node_allo[node.index]) == 1) for node in nodes):

    #     # 随机选择区块
    #     selected_block = random.choice(blocks)
        
    #     # 随机选择节点
    #     selected_node = random.choice(nodes)

    #     # 将区块分配给节点
    #     assign_block_to_node(selected_block, selected_node, block_node_allo)

    for node in nodes:
        while node.Sr >= max(block.Si for block in blocks) and not np.all(np.array(block_node_allo[node.index]) == 1):
            cond_blocks = filter(lambda block: block_node_allo[node.index][block.index] == 0, blocks)
            select_block = random.choice(list(cond_blocks))

            # 将区块分配给节点
            assign_block_to_node(select_block, node, block_node_allo)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
#####################################################################################################
# 两步式贪心算法-2018，相关函数

# 计算贪心算法-2018中单个区块的权重函数：f(i,j) ,输入 nodes、block、block_node_allo，输出 block.weightFij 一维列表，长度为j
def calculate_block_weightFij(nodes,block,block_node_allo):

    # 从 block_node_allo 中提取出存放了当前区块的节点列表
    node_assigned = np.where(np.array([row[block.index] for row in block_node_allo]) != 0)[0]

    # 初始化
    block.weightFij = []

    # f(i,j)：存放的是在将当前区块放在节点 j 后，所有节点访问当前区块的成本和
    # 对 nodes 进行两次遍历
    # 第一层计算把区块 bi 放到节点 vj 后的权重函数，无论是否已经在 block_node_allo 中分配过
    # 第二层求出最小的 Cki 并累加，与 block_node_allo 中的分配进行比较
    for j in range(len(nodes)):
        weightFij = 0
        for node in nodes:
            min_Cki = min( [node.Tjk[j]] + [node.Tjk[k] for k in node_assigned])
            weightFij += min_Cki * block.Si * node.fij_NgetB[block.index]
        block.weightFij.append(weightFij)

# 计算贪心算法-2018中单个区块的 δi_1 （此处用Epsilon代替）
def calculate_block_Epsilon_1(block:Block,nodes,block_node_allo):

    # 去除剩余空间小于当前区块大小的节点对应的 block.weightFij
    weightFij_copy = []
    weightFij_copy_index = []

    for index, value in enumerate(block.weightFij):
        if nodes[index].Sr >= block.Si and block_node_allo[index][block.index] == 0:      
            weightFij_copy.append(value)
            weightFij_copy_index.append(index)

    if len(weightFij_copy) == 1:
        return weightFij_copy_index[0],weightFij_copy[0], block.Epsilon[0]
    
    if len(weightFij_copy) == 0:

        # 表示这个区块找不到合适的节点放置，两种情况：区块已经放置到了全部的节点、未放置的节点没有足够的空间
        return -1,-1,block.Epsilon[0]

    # 对列表进行排序，并获取最小和第二小的值
    sorted_weightFij = sorted(weightFij_copy)
    secondSmallest_weightFij,smallest_weightFij = sorted_weightFij[1],sorted_weightFij[0]

    # 找最小的值和对应索引
    min_index,min_value = 0,weightFij_copy[0]
    for index, value in enumerate(weightFij_copy):
        if value < min_value:
            min_value = value
            min_index = index

    return weightFij_copy_index[min_index],smallest_weightFij,secondSmallest_weightFij-smallest_weightFij

# 计算贪心算法-2018中单个区块的 δi_2 （此处用Epsilon代替）
def calculate_block_Epsilon_2(block):

    return block.Ci - block.min_weightFij
###############################################################################################################
# 两步式贪心算法-2018，输出分配结果
def twoStepsGreedy2018_block_allocation(blocks:list[Block], nodes:list[Node]):

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 初始化区块的备份次数
    for block in blocks:
        block.Delta_i = 0

    # 初始化区块并计算区块的 f（i,j） 和 Epsilon_1
    for block in blocks:
        block.Delta_i = block.min_weightFij = block.Ci = 0
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)

    # 贪心算法-2018第一步
    while any(block.Delta_i == 0 for block in blocks):

        # 选择 Epsilon_1 最大的区块和节点
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Epsilon[0])      
        selected_node = nodes[selected_block.min_weightFij_index]

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

            # 更新区块 Ci 的值
            selected_block.Ci = selected_block.min_weightFij
        else:

            # 重新计算当前区块的 f（i,j） 和 Epsilon_1，计算时去掉空间不足的节点
            selected_block.min_weightFij_index,selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)

    # print(block_node_allo)
    
    # 贪心算法-2018第二步
    # 再次计算区块的 f（i,j） 和 Epsilon_2
    for block in blocks:
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)
        block.Epsilon[1] = calculate_block_Epsilon_2(block)

    # 下面的注释有问题，max（）报错是因为所有区块的min_weightFij都为-1，但是当满足while条件时weightFij应该不都为-1，加了if判断之后不再报错

    # 区块分配的条件：存在一个节点的剩余空间大于最大的区块大小，并且此节点上还未分配一整个区块链，由于2018CU的方法是以区块为出发点，所以还需要在循环中继续判断
    while any(node.Sr >= max(block.Si for block in blocks) and not np.all(np.array(block_node_allo[node.index]) == 1) for node in nodes):

        # 选择 Epsilon_2 最大的区块和节点，如果没有满足的区块（即还能满足上面循环条件，但要么某一区块已经在所有节点备份，要么未备份的节点空间已经不足）就停止分配
        if len( list(filter(lambda block: block.min_weightFij != -1, blocks))) == 0:
            print('All blocks min_weightFij == -1')
            break
        selected_block = max( filter(lambda block: block.min_weightFij != -1, blocks), key=lambda block: block.Epsilon[1])

        # 更新当前的选择的区块的属性后再选节点
        selected_block.min_weightFij_index,selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)
        selected_node = nodes[selected_block.min_weightFij_index]

        # 所选节点的剩余空间大于区块的大小，在计算Epsilon_1时已经进行过判断
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

            # 更新区块 Ci 的值
            selected_block.Ci = selected_block.min_weightFij

            # 更新所有区块的 f（i,j）、Epsilon_1 和 Epsilon_2
            calculate_block_weightFij(nodes,selected_block,block_node_allo)
            selected_block.min_weightFij_index,selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)
            selected_block.Epsilon[1] = calculate_block_Epsilon_2(selected_block)
            
            # print(block_node_allo)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
#####################################################################################################################################################
# 两步式贪心算法-FijAndPb，输出分配结果
def twoStepsGreedyFijAndPb_block_allocation(blocks, nodes):

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 初始化区块并计算区块的 f（i,j） 和 Epsilon_1
    for block in blocks:
        block.Delta_i = block.min_weightFij = block.Ci = 0
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)

    # 计算节点和区块的能力
    calculate_capabilities(blocks, nodes)

    # 第一步
    while any(block.Delta_i == 0 for block in blocks):

        # 选择Pb最大的区块和 weightFij 最小的节点
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Pb)      
        selected_node = nodes[selected_block.min_weightFij_index]

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

        else:

            # 重新计算当前区块的 f（i,j） 和 Epsilon_1，计算时去掉空间不足的节点
            selected_block.min_weightFij_index,selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)


    # 第二步

    # 再次计算区块的 f（i,j）
    for block in blocks:
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)

    # 再次计算节点和区块的能力
    calculate_capabilities(blocks, nodes)

    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):

        # 选择 Pb 最大的区块和节点
        selected_block = max(filter(lambda block: block.min_weightFij != -1, blocks), key=lambda block: block.Pb)
        block = selected_block
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)
        selected_node = nodes[selected_block.min_weightFij_index]

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

            # 更新所有区块的 f（i,j）、Epsilon_1 和 Pb
            # for block in blocks:

            calculate_block_weightFij(nodes,block,block_node_allo)
            block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)
            block.Pb = calculate_block_capability(block=block)

    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
###############################################################################################################################
# 两步式贪心算法-FijAndPv，输出分配结果
def twoStepsGreedyFijAndPv_block_allocation(blocks, nodes):

    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 初始化区块并计算区块的 f（i,j） 和 Epsilon_1
    for block in blocks:
        block.Delta_i = block.min_weightFij = block.Ci = 0
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)

    # 计算节点和区块的能力
    calculate_capabilities(blocks, nodes)

    # 贪心算法-2018第一步
    while any(block.Delta_i == 0 for block in blocks):

        # 选择 Epsilon_1 最大的区块和 Pv 最大的节点
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Epsilon[0])      
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)
            # 更新区块 Ci 的值
            selected_block.Ci = selected_block.min_weightFij
            # 计算节点和区块的能力
            calculate_capabilities(blocks, nodes)   

        else:

            # 重新计算当前区块的 f（i,j） 和 Epsilon_1，计算时去掉空间不足的节点
            selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)


    # 第二步

    # 再次计算区块的 f（i,j）
    for block in blocks:
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)
        block.Epsilon[1] = calculate_block_Epsilon_2(block)

    # 再次计算节点和区块的能力
    calculate_capabilities(blocks, nodes)

    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):

        # 选择 Epsilon_2 最大的区块和 Pv 最大的节点
        selected_block = max(blocks, key=lambda block: block.Epsilon[1])
        selected_node = max(filter(lambda node: node.Sr >= selected_block.Si, nodes), key=lambda node: node.Pv)

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)
            # 更新区块 Ci 的值
            selected_block.Ci = selected_block.min_weightFij
            # 再次计算节点和区块的能力
            calculate_capabilities(blocks, nodes)
            
            # 更新所有区块的 f（i,j）、Epsilon_1 和 Pv
            for block in blocks:
                calculate_block_weightFij(nodes,block,block_node_allo)
                block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)
                block.Epsilon[1] = calculate_block_Epsilon_2(block)


    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
####################################################################################################################
# 两步式贪心-f*T/meanT的区块分配方案

def calculate_block_fTmeanT(nodes,block,block_node_allo):

    # 从 block_node_allo 中提取出存放了当前区块的节点列表
    node_assigned = np.where(np.array([row[block.index] for row in block_node_allo]) != 0)[0]

    # 初始化
    block.Sv = []

    # 对 nodes 进行两次遍历
    # 第一层计算把区块 bi 放到节点 vj 后的权重函数，无论是否已经在 block_node_allo 中分配过
    # 第二层求出最小的 Cki 并累加，与 block_node_allo 中的分配进行比较
    for node in nodes:
        Tjk_list = [node.Tjk[k] for k in node_assigned]
        mean_Tjk = sum(Tjk_list)/len(Tjk_list)
        # Sv = mean_Tjk 
        Sv = mean_Tjk * node.fij_NgetB[block.index] / node.meanTjk 
        block.Sv.append(Sv)

def calculate_maxSv(nodes,block):
    # 去除剩余空间小于当前区块大小的节点对应的 block.Sv
    Sv_copy = []
    Sv_copy_index = []

    for index, value in enumerate(block.weightFij):
        if nodes[index].Sr >= block.Si:
            Sv_copy.append(value)
            Sv_copy_index.append(index)

    if len(Sv_copy) == 1:
        return Sv_copy_index[0]
    
    if len(Sv_copy) == 0:
        return -1
    
    max_Sv_index = Sv_copy_index[find_max_index(Sv_copy)] 
    return max_Sv_index

def find_max_index(lst):
    if len(lst) == 0:
        return None

    max_val = lst[0]
    max_index = 0

    for i in range(1, len(lst)):
        if lst[i] > max_val:
            max_val = lst[i]
            max_index = i

    return max_index

def greedyfTmeanT_block_allocation(blocks, nodes):
    
    block_node_allo = [[0] * len(blocks) for _ in range(len(nodes))]

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 初始化区块并计算区块的 f（i,j） 和 Epsilon_1
    for block in blocks:
        block.Delta_i = block.min_weightFij = 0
        calculate_block_weightFij(nodes,block,block_node_allo)
        block.min_weightFij_index,block.min_weightFij,block.Epsilon[0] = calculate_block_Epsilon_1(block,nodes,block_node_allo)

    # 第一步与2018年相同
    while any(block.Delta_i == 0 for block in blocks):

        # 选择 Epsilon_1 最大的区块和节点
        selected_block = max(filter(lambda block: block.Delta_i == 0, blocks), key=lambda block: block.Epsilon[0])      
        selected_node = nodes[selected_block.min_weightFij_index]


        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

        else:

            # 重新计算当前区块的 f（i,j） 和 Epsilon_1，计算时去掉空间不足的节点
            selected_block.min_weightFij_index,selected_block.min_weightFij,selected_block.Epsilon[0] = calculate_block_Epsilon_1(selected_block,nodes,block_node_allo)


    # 第二步，计算所有节点到已放区块节点的 f*Tjkmin/meanTjk，作为区块的属性，计算 m*n
    # 选取Pb最大的区块，和上述最大的节点，更新区块分配
    # 更新Pb和当前区块各节点的 f*T/meanTjk
    for block in blocks:
        block.Pb = calculate_block_capability(block)
        calculate_block_fTmeanT(nodes,block,block_node_allo)
        block.max_Sv_index = calculate_maxSv(nodes,block)

    while any(node.Sr >= max(block.Si for block in blocks) for node in nodes):

        # 选择 pb 最大的区块和 Sv 最大的节点
        selected_block = max(blocks, key=lambda block: block.Pb)

        # 如果要根据当前选的区块，再选节点，条件要在区块选择后再计算
        selected_block.max_Sv_index = calculate_maxSv(nodes,selected_block)
        selected_node = nodes[selected_block.max_Sv_index]

        # 所选节点的剩余空间大于区块的大小
        if selected_node.Sr > selected_block.Si:

            # 将区块分配给节点
            assign_block_to_node(selected_block, selected_node, block_node_allo)

            # 更新当前区块的 Pb、Sv 和 max_Sv_index
            selected_block.Pb = calculate_block_capability(selected_block)
            calculate_block_fTmeanT(nodes,selected_block,block_node_allo)


    # 将二维数组转换为矩阵
    block_node_allo = np.array(block_node_allo)

    return block_node_allo
########################################################################################################################
# myTest的区块分配方案
def myTest_block_allocation(blocks, nodes, Node_Tjk, Node_meanTj):
    
    nodeNum = len(nodes)
    blockNum = len(blocks)
    
    #区块和节点选择列表
    select_node_list = []

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    block_node_allo = np.zeros((nodeNum, blockNum))
    #定义临近节点
    print(np.percentile(Node_Tjk,40))
    near_node = (Node_Tjk < np.percentile(Node_Tjk,40)).astype('int') + 10*np.identity(nodeNum)
    
    print("Step 1")
    '''区块属性'''
    Pb = np.zeros(blockNum)
    for block in blocks:
        Pb[block.index] = sum(block.Wij)
    Pb_argsort = np.argsort(-Pb) #降序排列
    
    for selected_block_index in Pb_argsort:
        Pv = {} #节点需求除以节点平均通信能力
        selected_block = blocks[selected_block_index]
        for j in range(nodeNum):
            if(block_node_allo[j, selected_block_index] == 0 and selected_block.Si < nodes[j].Sr):
                #计算的每个节点的需求（包括附近节点的需求/不包括已经放置区块的节点）
                node_need = sum(selected_block.Wij * near_node[:,j])
                Pv[j] = node_need / Node_meanTj[j]
        # print(selected_block.Wij)
        # print(Pv)
        if (len(Pv) != 0):
            selected_node_index = max(Pv, key=Pv.get)
            select_node_list.append(selected_node_index)
            # print(selected_block_index, selected_node_index)
            selected_node = nodes[selected_node_index]
            assign_block_to_node(selected_block, selected_node, block_node_allo)
            # Pb[selected_block_index] -= selected_block.Wij[selected_node_index]
            
    print("Step 2")
    blockSizeMax = max(block.Si for block in blocks)
    while any(node.Sr >= blockSizeMax for node in nodes):
        selected_block_index = np.argmax(Pb)
        selected_block = blocks[selected_block_index]
        
        Pv = {} #节点需求除以节点平均通信能力
        for j in range(nodeNum):
            if(block_node_allo[j, selected_block_index] == 0 and selected_block.Si < nodes[j].Sr):
                #计算的每个节点的需求（包括附近节点的需求/不包括已经放置区块的节点）
                node_need = sum(selected_block.Wij * near_node[:,j] * (1 - 1 * block_node_allo[:,selected_block.index]))
                Pv[j] = node_need / Node_meanTj[j] * min(nodes[j].Tjk[np.where(block_node_allo[:,selected_block_index])])
        # print(selected_block.Wij)
        # print(Pv)
        if (len(Pv) != 0):
            selected_node_index = max(Pv, key=Pv.get)
            select_node_list.append(selected_node_index)
            # print(selected_block_index, selected_node_index)
            selected_node = nodes[selected_node_index]
            assign_block_to_node(selected_block, selected_node, block_node_allo)
            Pb[selected_block_index] /= (selected_block.Delta_i)
            # Pb[selected_block_index] -= selected_block.Wij[selected_node_index]
        else:
            Pb[selected_block_index] = 0
        


    return block_node_allo
#####################################################################################################################
# 分配：myTest_0811
def myTest_block_allocation_0811(blocks, nodes, Node_Tjk, Node_meanTj):
    
    def choice_node(selected_block_index):
        Pv_j = [] #节点序号
        Pv_value = []#节点需求除以节点平均通信能力 
        # for j in range(nodeNum):
        # for j in demand_block[selected_block_index]:
        for j in range(len(nodes)):   
            if(block_node_allo[j, selected_block_index] == 0 and selected_block.Si < nodes[j].Sr):
                #计算的每个节点的需求（包括附近节点的需求/不包括已经放置区块的节点）
                if (sum(block_node_allo[:,selected_block.index]) == 0):
                    node_need = sum(selected_block.Wij * near_node[:,j])
                    Pv_j.append(j)
                    Pv_value.append(node_need / Node_meanTj[j])
                else:
                    node_need = sum(selected_block.Wij * near_node[:,j] * (1 - 2 * block_node_allo[:,selected_block.index]))
                    # if (node_need > 0):
                    Pv_j.append(j)
                    Pv_value.append(node_need / Node_meanTj[j] * min(nodes[j].Tjk[np.where(block_node_allo[:,selected_block_index])])) 

        if (len(Pv_j) != 0):
            selected_node_index = Pv_j[np.argmax(Pv_value)]
            # Pv_j, Pv_value = np.array(Pv_j), np.array(Pv_value)
            # select_nodes = np.where(Pv_value > max(Pv_value) * 0.8)
            # p = Pv_value[select_nodes] - min(Pv_value) + 1
            # p = p/sum(p)
            # Pv_value = Pv_value / sum(Pv_value)
            # selected_node_index = np.random.choice(Pv_j[select_nodes], size = 1, p = p)[0]
            
            select_node_list.append(selected_node_index)
            # Pb[selected_block_index] = Pb[selected_block_index] - (selected_block.Wij[selected_node_index]*(5 - selected_block.Delta_i))
            # Pb[selected_block_index] = (Pb[selected_block_index] - selected_block.Wij[selected_node_index] * 2)/(selected_block.Delta_i + 1)
            # Pb[selected_block_index] = Pb[selected_block_index] - selected_block.Wij[selected_node_index] * (selected_block.Delta_i + 1)
            Pb[selected_block_index] /= (selected_block.Delta_i + 1)
            return selected_node_index
        else:
            Pb[selected_block_index] = 0
            return -1
    
    blockNum = len(blocks)
    nodeNum = len(nodes)
    block_node_allo = np.zeros((nodeNum, blockNum))

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 初始化区块的备份次数
    for block in blocks:
        block.Delta_i = 0

    #定义临近节点
    # print(np.percentile(Node_Tjk, 40))
    near_node = 15 * np.identity(nodeNum)\
                + 5 * (Node_Tjk < np.percentile(Node_Tjk, 20)).astype('int')\
                + 1 * (Node_Tjk < np.percentile(Node_Tjk, 40)).astype('int')\
                # + 1 * (Node_Tjk < np.percentile(Node_Tjk, 60)).astype('int')
                
    
    '''区块属性'''
    Pb = np.zeros(blockNum)
    for block in blocks:
        Pb[block.index] = sum(block.Wij) + 100
    Pb_argsort = np.argsort(-Pb) #降序排列10
    
    # Pb_mean = Pb / nodeNum #节点对该区块的平均需求
    demand_block = [] #超过阈值的需求节点序号
    for block in blocks:
        demand_block.append(np.where(block.Wij > np.percentile(block.Wij, 30))[0])
    
    #区块和节点选择列表
    select_block_list = []
    select_node_list = []
    
    # print("Step 1")
    for selected_block_index in Pb_argsort:
        
        selected_block = blocks[selected_block_index]
        selected_node_index = choice_node(selected_block_index)
        
        if (selected_node_index != -1):
            selected_node = nodes[selected_node_index]
            assign_block_to_node(selected_block, selected_node, block_node_allo)
            
    # print("Step 2")
    blockSizeMax = max(block.Si for block in blocks)

    # 区块分配（循环）的条件：存在一个节点的剩余空间大于最大的区块大小，并且此节点上还未分配一整个区块链
    while any(node.Sr >= max(block.Si for block in blocks) and not np.all(np.array(block_node_allo[node.index]) == 1) for node in nodes):
        selected_block_index = np.argmax(Pb)
        selected_block = blocks[selected_block_index]
        
        selected_node_index = choice_node(selected_block_index)
        if (selected_node_index != -1):
            selected_node = nodes[selected_node_index]
            assign_block_to_node(selected_block, selected_node, block_node_allo)
        
    return block_node_allo
####################################################################################################################
# 分配：SNBA
# 备份第一份区块链后，每个节点的剩余空间将优先存储需求概率最大几个区块

def SNBA_allocation(blocks,nodes):

    blockNum = len(blocks)
    nodeNum = len(nodes)
    block_node_allo = np.zeros((nodeNum, blockNum))

    # 初始化节点的剩余空间
    for node in nodes:
        node.Sr = node.capacity 

    # 第一次备份
    for block in blocks:

        # select_node = 最大的BbyN 且 Sr>Si
        cond_nodes = filter(lambda node: node.Sr >= block.Si, nodes)
        select_node = max(cond_nodes, key=lambda node: node.fij_NgetB[block.index])

        # 将区块分配给节点
        assign_block_to_node(block, select_node, block_node_allo)

    # 后续
    for node in nodes:
        while node.Sr >= max(block.Si for block in blocks) and not np.all(np.array(block_node_allo[node.index]) == 1):
            cond_blocks = filter(lambda block: block_node_allo[node.index][block.index] == 0, blocks)
            select_block = max(cond_blocks, key=lambda block: block.fij_BbyN[node.index])

            # 将区块分配给节点
            assign_block_to_node(select_block, node, block_node_allo)

    return block_node_allo