import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

filepath2='D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness2_main3_4.0.txt'
filepath1='D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness1_main3_4.0.txt'
def plot_user(filepath,label):
    y_data=[]
    with open(filepath, 'r') as file:
        lines = file.readlines()
        lines = [float(value) for line in lines for value in line.strip("[]\n").split(", ")]
        y_data=lines
    
    plt.style.use('ggplot')
    plt.grid(True)
    plt.title('Allocation')
    plt.legend(loc='upper right')

    rolling_intv =1
    df = pd.DataFrame(y_data)
    y_data_new = list(np.hstack(df.rolling(rolling_intv, min_periods=1).mean().values))
    xdata = list(range(len(y_data_new)))
    
    plt.plot(xdata, y_data_new, label=label)
    plt.xlabel('Episode')
    plt.ylabel('best_fitness')
    plt.legend()
    


y_data=[]
y_data1=[]

#with open('D:/reinforcement-code/output2.txt', 'r') as file:
with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness11_mean_1_main3_4.0.txt', 'r') as file:
#with open('D:/reinforcement-code/reward_for_DQN.txt', 'r') as file:
#with open('D:/reinforcement-code/reward_for_perDQN.txt', 'r') as file:
    lines = file.readlines()
    lines = [float(value) for line in lines for value in line.strip("[]\n").split(", ")]
    y_data1=lines



    '''for line in lines:
        value = float(line.strip())
        y_data.append(value)  # 去除行尾的换行符'''

with open('D:/python-code/GreedyAndRandom_0705-master/recombine/results_mine/best_fitness22_mean_2_main3_4.0.txt', 'r') as file:
#with open('D:/reinforcement-code/reward_for_DQN.txt', 'r') as file:
#with open('D:/reinforcement-code/reward_for_perDQN.txt', 'r') as file:
    lines = file.readlines()
    lines = [float(value) for line in lines for value in line.strip("[]\n").split(", ")]
    y_data2=lines
    '''for line in lines:
        value = float(line.strip())
        y_data1.append(value)  # 去除行尾的换行符'''


plt.style.use('ggplot')
plt.grid(True)
plt.title('Allocation')
plt.legend(loc='upper right')

rolling_intv =1
df1 = pd.DataFrame(y_data1)
df2 = pd.DataFrame(y_data2)
y_data_new1 = list(np.hstack(df1.rolling(rolling_intv, min_periods=1).mean().values))
y_data_new2 = list(np.hstack(df2.rolling(rolling_intv, min_periods=1).mean().values))
xdata1 = list(range(len(y_data_new1)))
xdata2 = list(range(len(y_data_new2)))

plt.plot(xdata1, y_data_new1, label='method_mix')
plt.plot(xdata2,y_data_new2,label='method_GA')

plt.xlabel('Episode')
plt.ylabel('fitness')
plt.legend()
plt.show()

plot_user(filepath1,"mix")
plot_user(filepath2,"GA")
plt.show()