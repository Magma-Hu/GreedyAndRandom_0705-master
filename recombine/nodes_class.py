# 节点类
import networkx as nx
import numpy as np

#计算算法函数运行时间的装饰器
import time,inspect
def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        arg_names = inspect.getfullargspec(func).args
        if 'Algorithm' in arg_names:
            Algorithm = args[arg_names.index('Algorithm')]
            print(f"{Algorithm} 运行时间为: {execution_time:.6f} 秒")
        else:
            print(f"{func.__name__} 运行时间为: {execution_time:.6f} 秒")
        return result
    return wrapper

# 生成符合指定范围正态分布的随机数:均值,标准差,下界,上界,随机数组形状
def truncated_normal(mean, std_dev, lower_bound, upper_bound, size=None):
    samples = np.random.normal(mean, std_dev, size)
    samples = np.clip(samples, lower_bound + 1e-8, upper_bound - 1e-8)
    return samples

class Node:
    def __init__(self, index, capacity=0, Tjk=[], meanTjk=0):
        self.index = index
        self.capacity = capacity
        self.Sr = capacity
        self.Tjk = Tjk
        self.meanTjk = meanTjk
        self.Tji = None
        self.fij_NgetB = []
        self.Pv = 0
        
    def print_attributes(cls):
        attributes = [attr for attr in cls.__dict__ if not attr.startswith('__')]
        for attr in attributes:
            value = getattr(cls, attr)
            print(f"{attr}: {value}")

    def gen_NgetBFre(self,blockNum=0):            
        # 随机生成节点访问所有区块的概率，范围在[0, 1]之间的均匀分布，并进行标准化处理，总概率为1(有概率比1小一点)
        # ！频率完全随机有问题，因为按照真实情况，较近的区块可能频率很低
        # NgetBFre = np.random.rand(blockNum)

        # 随机生成节点访问所有区块的概率，范围在[0, 1]之间的正态分布
        mean,std_dev,lower_bound,upper_bound,size = 2, 1.5, 0, 4, blockNum
        NgetBFre = truncated_normal(mean, std_dev, lower_bound, upper_bound, size)

        # NgetBFre /= np.sum(NgetBFre)
        self.fij_NgetB = NgetBFre

# 初始化Node的所有属性，属性值从文件中提取
def NodeInit(NodeNum = 0,Node_capacity = None,Node_Tjk = None,Node_Tj = None,blockNum = None):

    nodes = []

    for j in range(NodeNum):
        newNode = Node(index=j,capacity=Node_capacity[j],Tjk = Node_Tjk[j],meanTjk= Node_Tj[j])
        newNode.gen_NgetBFre(blockNum=blockNum)
        nodes.append(newNode)

    return nodes

# 从 GML 文件中提取容量、时延和路径
def extract_node_data_from_gml(file_path,nodeNum):

    # 从 GML 文件中导入图
    G = nx.read_gml(file_path)
    
    # 读取节点数
    NodeNum = G.number_of_nodes()

    # 导出 G 中节点的大小属性，用来代表节点的初始存储空间
    # 一维列表转 np 的数组
    Node_capacity = [G.nodes[str(i)]['size'] for i in range(NodeNum)]
    Node_capacity_array=np.array(Node_capacity) 

    # 导出 G 中节点到其他节点的最短路径长度，用来代表节点间的通信时延
    # 先访问列表再访问字典，如：node_path[0].get('1')，代表节点 0 到节点 1 的路径长度,没有路径则返回 None
    Node_Tjk = [eval(G.nodes[str(i)]['pathLength']) for i in range(NodeNum)]
    
    # 一维列表一维字典 转 二维列表
    Node_Tjk_list = []
    for startNode in range(NodeNum):
        Node_Tjk_list.append([Node_Tjk[startNode].get(str(endNode)) for endNode in range(NodeNum)])

    # 二维列表转np的数组，没有路径的节点通信时延标为inf
    Node_Tjk_array=np.array(Node_Tjk_list)    
    Node_Tjk_array[Node_Tjk_array == None] = np.inf
    if np.inf in Node_Tjk_array:
        raise Exception("节点间有路径不通")

    # Node_Tjk_array每一行求和得到Node_Tj_array
    Node_meanTj_array=np.sum(np.where(Node_Tjk_array != np.inf, Node_Tjk_array, 0), axis=1)/nodeNum

    return NodeNum,Node_capacity_array,Node_Tjk_array,Node_meanTj_array