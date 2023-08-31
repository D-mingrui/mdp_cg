from gurobipy import *
from run_data import *


[orders, restaurants] = read_data(r'C:\Users\32684\Desktop\mdp_data\test\order1.txt',
                                  r'C:\Users\32684\Desktop\mdp_data\test\restaurant1.txt')
order_num = len(orders)     # 订单的数量
service_time = 2    # 每个订单顾客节点的服务时间
rider_num = 2   # 可用的骑手数量
max_order = 6   # 每个骑手最多配送的订单数量
speed = 240     # 骑手行驶的速度 米/分钟
f_cost = 1      # 骑手行驶的单位距离成本

set_P = [i for i in range(1, order_num + 1)]    # 集合P
set_D = [i for i in range(order_num + 1, 2 * order_num + 1)]    # 集合D
set_N = [i for i in range(2 * order_num + 2)]   # 集合N
set_K = [k for k in range(rider_num)]
start_node = 0
dest_node = 2 * order_num + 1

s_i = {}    # 餐馆i的单位延迟时间惩罚成本
l_i = {}    # 餐馆i的配送时效要求
B_i = {}    # 订单i的可取餐时间
depot = [6000, 6000]    # 配送中心的坐标
node_cor_x = {}     # 记录所有节点的横坐标
node_cor_y = {}     # 记录所有节点的纵坐标
node_cor_x[0] = depot[0]
node_cor_x[2 * order_num + 1] = depot[1]
node_cor_y[0] = depot[0]
node_cor_y[2 * order_num + 1] = depot[1]
big_M = 1000000

for i in set_P:
    B_i[i] = orders[i - 1].ready_time
    node_cor_x[i] = orders[i - 1].cor_x
    node_cor_y[i] = orders[i - 1].cor_y
    cur_res = restaurants[orders[i - 1].restaurant - 1]
    s_i[i] = cur_res.penalty
    l_i[i] = cur_res.time
    node_cor_x[i + order_num] = cur_res.cor_x
    node_cor_y[i + order_num] = cur_res.cor_y

d_i_j = {}  # 记录各节点之间的距离
t_i_j = {}  # 记录各节点之间的行驶时间
for i in set_N:
    for j in set_N:
        d_i_j[i, j] = abs(node_cor_x[i] - node_cor_x[j]) + abs(node_cor_y[i] - node_cor_y[j])
        t_i_j[i, j] = d_i_j[i, j] / speed
d_i_j[start_node, dest_node] = big_M
t_i_j[start_node, dest_node] = d_i_j[start_node, dest_node] / speed
d_i_j[dest_node, start_node] = big_M
t_i_j[dest_node, start_node] = d_i_j[dest_node, start_node] / speed

q_j = [0]   # 记录各节点的取送餐情况
for i in set_P:
    q_j.append(1)
for i in set_D:
    q_j.append(1)
q_j.append(0)

model = Model('origin_model')

route_set = {}  # 可行路径集合






















