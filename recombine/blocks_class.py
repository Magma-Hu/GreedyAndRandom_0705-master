# 区块类

import numpy as np

class Block:
    def __init__(self, index=0, blockSize=0, blockTime=0):
        self.index = index
        self.Si = blockSize
        self.Time = blockTime
        self.Delta_i = 0
        self.Pb = 0
        self.Wij = []
        self.fij_BbyN = [] 
        self.weightFij = [] # 长度为j的一维列表，f(i,j)
        self.min_weightFij = 0
        self.min_weightFij_index = 0
        self.Epsilon = [0,0] #
        self.Ci = 0 # 记录区块上一次的最小权重函数值 f(i,si_1)
        self.Sv = [] # 各节点的 f*Tjkmin/meanTjk
        self.max_Sv_index = 0  

    def print_attributes(cls):
        attributes = [attr for attr in cls.__dict__ if not attr.startswith('__')]
        for attr in attributes:
            value = getattr(cls, attr)
            print(f"{attr}: {value}")

    def cal_BbyNFre(self,nodes=None):            
        # 计算区块被节点访问的概率，由节点访问区块的概率计算而来，概率值不定
        if nodes == None:
            raise Exception("节点未初始化")
        BbyNFre =  []
        for  j in range(len(nodes)):
            BbyNFre.append(nodes[j].fij_NgetB[self.index])
        self.fij_BbyN = np.array(BbyNFre)

        self.cal_Wij()

    def cal_Wij(self):
        # Block[i].Wij[j] = Block[i].Si * Block[i].fij_BbyN[j]
        self.Wij = self.fij_BbyN*self.Si


#生成区块的属性
def gen_block(blockNum, seed=1037, saveBlock=True):
    # np.random.seed(seed)
    
    # 生成区块大小，服从正态分布
    # ！区块的大小和节点的存储空间大小要相匹配
    blockSize = np.random.randn(blockNum) + 8
    
    # 生成区块的生成时间参数，按指数增长，blockNum和区块的生成前后顺序有关
    blockTime = np.exp((np.arange(blockNum) - blockNum + 1) * 0.1)
    
    if saveBlock:
        # 保存区块信息到文件
        np.savez('D:/python-code/GreedyAndRandom_0705-master/Model/BlockInfo/{blockNum}blocksInfo.npz'.format(blockNum=blockNum), 
                 blockSize=blockSize,blockTime=blockTime)
    
    return blockNum, blockSize, blockTime

# 初始化区块的所有属性
def BlockInit(blockNum = 0,blockSize = None,blockTime = None,nodes = None):

    Blocks = []

    for i in range(blockNum):
        newBlock = Block(index=i,blockSize=blockSize[i],blockTime=blockTime[i])
        newBlock.cal_BbyNFre(nodes=nodes)
        Blocks.append(newBlock)

    return Blocks