import numpy as np

# 定义待优化的函数，这里以一个简单的二次函数为例
def objective_function(x):
    return x**2 - 4*x + 4

# 模拟退火算法
def simulated_annealing(objective_function, initial_solution, initial_temperature, cooling_rate, iterations):
    current_solution = initial_solution
    best_solution = current_solution
    current_temperature = initial_temperature

    for i in range(iterations):
        # 生成一个随机解，这里采用简单的正态分布方式
        candidate_solution = current_solution + np.random.normal(0, 1)

        # 计算当前解和候选解的能量差
        energy_difference = objective_function(candidate_solution) - objective_function(current_solution)

        # 如果候选解的能量更低或者以一定概率接受能量更高的候选解，则接受候选解
        if energy_difference < 0 or np.random.rand() < np.exp(-energy_difference / current_temperature):
            current_solution = candidate_solution

        # 更新最佳解
        if objective_function(current_solution) < objective_function(best_solution):
            best_solution = current_solution

        # 降低温度
        current_temperature *= cooling_rate

    return best_solution

# 参数设置
initial_solution = 0.0
initial_temperature = 100.0
cooling_rate = 0.99
iterations = 1000

# 调用模拟退火算法求解
best_solution = simulated_annealing(objective_function, initial_solution, initial_temperature, cooling_rate, iterations)
best_value = objective_function(best_solution)

print("最优解:", best_solution)
print("最优值:", best_value)
