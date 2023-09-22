from gurobipy import *
from new_run_data import *
from draw_picture import Draw
import time


origin_data_path = r'D:\资料\赵秋红导师组\本科毕设\文献\外卖配送\Li and Lim pdp_100\lc101.txt'
depot_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\50_lc_101_depot.txt'
pickup_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\50_lc_101_pickup.txt'
delivery_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\50_lc_101_delivery.txt'

# [depot_node, pickup_nodes, delivery_nodes] = generate_read_data(origin_data_path)
[depot_node, pickup_nodes, delivery_nodes] = read_data(depot_path, pickup_path, delivery_path)
order_num = len(pickup_nodes)     # 订单的数量
rider_num = 8   # 可用的骑手数量
max_order = 10   # 每个骑手最多配送的订单数量
speed = 2     # 骑手行驶的速度 米/分钟
f_cost = 1      # 骑手行驶的单位距离成本


set_P = [i for i in range(1, order_num + 1)]    # 集合P
set_D = [i for i in range(order_num + 1, 2 * order_num + 1)]    # 集合D
set_N = [i for i in range(2 * order_num + 2)]   # 集合N
set_K = [k for k in range(rider_num)]
start_node = 0
dest_node = 2 * order_num + 1

A_i = {}    # 订单i的可取餐时间
B_i = {}    # 订单i的最晚取餐时间
E_i = {}    # 订单i的最早送餐时间
F_i_hard = {}   # 订单i的最晚送餐时间
F_i_soft = {}   # 订单i的延迟成本开始计算时间
s_i = {}    # 餐馆i的单位延迟时间惩罚成本
service_time = {}   # 所有取餐和送餐节点的服务时间
depot = [depot_node.cor_x, depot_node.cor_y]    # 配送中心的坐标
node_cor_x = {}     # 记录所有节点的横坐标
node_cor_y = {}     # 记录所有节点的纵坐标
node_cor_x[0] = depot[0]
node_cor_x[2 * order_num + 1] = depot[0]
node_cor_y[0] = depot[1]
node_cor_y[2 * order_num + 1] = depot[1]
big_M = 100000

for i in set_P:
    A_i[i] = pickup_nodes[i - 1].early_time
    B_i[i] = pickup_nodes[i - 1].late_time
    E_i[i + order_num] = delivery_nodes[i - 1].early_time
    F_i_hard[i + order_num] = delivery_nodes[i - 1].late_time
    F_i_soft[i + order_num] = delivery_nodes[i - 1].cost_time
    s_i[i] = delivery_nodes[i - 1].penalty
    service_time[i] = pickup_nodes[i - 1].service_time
    service_time[i + order_num] = delivery_nodes[i - 1].service_time
    node_cor_x[i] = pickup_nodes[i - 1].cor_x
    node_cor_y[i] = pickup_nodes[i - 1].cor_y
    node_cor_x[i + order_num] = delivery_nodes[i - 1].cor_x
    node_cor_y[i + order_num] = delivery_nodes[i - 1].cor_y
service_time[start_node] = 0
service_time[dest_node] = 0

d_i_j = {}  # 记录各节点之间的距离
t_i_j = {}  # 记录各节点之间的行驶时间
for i in set_N:
    for j in set_N:
        d_i_j[i, j] = abs(node_cor_x[i] - node_cor_x[j]) + abs(node_cor_y[i] - node_cor_y[j])
        t_i_j[i, j] = d_i_j[i, j] / speed
d_i_j[start_node, dest_node] = big_M / 10
t_i_j[start_node, dest_node] = d_i_j[start_node, dest_node] / speed
d_i_j[dest_node, start_node] = big_M / 10
t_i_j[dest_node, start_node] = d_i_j[dest_node, start_node] / speed

q_j = [0]   # 记录各节点的取送餐情况
for i in set_P:
    q_j.append(1)
for i in set_D:
    q_j.append(1)
q_j.append(0)

start_time = time.time()

model = Model('origin_model')

X = {}  # x_i_j_k
Q = {}  # Q_i_k
L = {}  # L_i_k
D = {}  # D_i_k

for i in set_N:
    for j in set_N:
        for k in set_K:
            name_x = 'x_' + str(i) + '_' + str(j) + '_' + str(k)
            X[i, j, k] = model.addVar(0, 1, vtype=GRB.BINARY, name=name_x)

for i in set_N:
    for k in set_K:
        name_Q = 'Q_' + str(i) + '_' + str(k)
        Q[i, k] = model.addVar(0, vtype=GRB.CONTINUOUS, name=name_Q)

for i in set_N:
    for k in set_K:
        name_L = 'L_' + str(i) + '_' + str(k)
        L[i, k] = model.addVar(0, vtype=GRB.CONTINUOUS, name=name_L)

for i in set_D:
    for k in set_K:
        name_D = 'D_' + str(i) + '_' + str(k)
        D[i, k] = model.addVar(0, vtype=GRB.CONTINUOUS, name=name_D)

obj = LinExpr(0)
obj1 = LinExpr(0)
obj2 = LinExpr(0)
for i in set_N:
    for j in set_N:
        for k in set_K:
            obj1.addTerms(f_cost * d_i_j[i, j], X[i, j, k])
for i in set_P:
    for k in set_K:
        obj2.addTerms(s_i[i], D[i + order_num, k])
obj.add(obj1)
obj.add(obj2)
model.setObjective(obj, GRB.MINIMIZE)

# c5
for i in set_P:
    expr = LinExpr(0)
    for j in set_N:
        for k in set_K:
            expr.addTerms(1, X[i, j, k])
    model.addConstr(expr == 1, 'c5')
    expr.clear()

# c6
for i in set_P:
    for k in set_K:
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for j in set_N:
            expr1.addTerms(1, X[i, j, k])
            expr2.addTerms(1, X[i + order_num, j, k])
        model.addConstr(expr1 - expr2 == 0, 'c6')
        expr1.clear()
        expr2.clear()

# c7
for k in set_K:
    expr = LinExpr(0)
    for j in set_N:
        expr.addTerms(1, X[start_node, j, k])
    model.addConstr(expr == 1, 'c7')
    expr.clear()

# c8
for k in set_K:
    expr = LinExpr(0)
    for i in set_N:
        expr.addTerms(1, X[i, dest_node, k])
    model.addConstr(expr == 1, 'c8')
    expr.clear()

# c9
for i in set_P + set_D:
    for k in set_K:
        expr1 = LinExpr(0)
        expr2 = LinExpr(0)
        for j in set_N:
            expr1.addTerms(1, X[j, i, k])
            expr2.addTerms(1, X[i, j, k])
        model.addConstr(expr1 - expr2 == 0, 'c9')

# c13  -1
for i in set_P:
    for k in set_K:
        model.addConstr(L[i, k] <= B_i[i], 'c13')

# c13  -2
for i in set_P:
    for k in set_K:
        model.addConstr(L[i, k] >= A_i[i], 'c13')

# c14  -1
for i in set_D:
    for k in set_K:
        model.addConstr(L[i, k] <= F_i_hard[i], 'c14')

# c14  -2
for i in set_D:
    for k in set_K:
        model.addConstr(L[i, k] >= E_i[i], 'c14')

# c15
for i in set_P:
    for k in set_K:
        model.addConstr(L[i, k] + t_i_j[i, i + order_num] <= L[i + order_num, k], 'c15')

# c16
for k in set_K:
    model.addConstr(L[start_node, k] <= L[dest_node, k], 'c16')

# c17
for i in set_N:
    for k in set_K:
        model.addConstr(Q[i, k] <= max_order * 2, 'c17')

# c19
for i in set_P:
    for k in set_K:
        model.addConstr(D[i + order_num, k] >= L[i + order_num, k] - F_i_soft[i + order_num], 'c19')

# c21
for i in set_N:
    for j in set_N:
        for k in set_K:
            model.addConstr(Q[j, k] >= Q[i, k] + q_j[j] + big_M * (X[i, j, k] - 1), 'c21')

# c23
for i in set_N:
    for j in set_N:
        for k in set_K:
            model.addConstr(L[j, k] >= L[i, k] + t_i_j[i, j] + big_M * (X[i, j, k] - 1) + service_time[i], 'c23')

# model.setParam('TimeLimit', 200)
model.optimize()
model.write(r'C:\Users\32684\Desktop\model.lp')

end_time = time.time()
print('求解时间：%f' % (end_time - start_time))

path = [[] for k in set_K]
arrive_time = [[] for k in set_K]
for k in set_K:
    for i in set_N:
        for j in set_N:
            if X[i, j, k].X > 0.99:
                path[k].append(i)
                arrive_time[k].append(L[i, k].X)
    path[k].append(dest_node)
    arrive_time[k].append(L[dest_node, k].X)
    arrive_time[k], path[k] = zip(*sorted(zip(arrive_time[k], path[k])))

with open(r'C:\Users\32684\Desktop\solver_solution.txt', 'w') as f:
    for k in set_K:
        print('第%d个骑手的路线：\n' % k, file=f)
        print(path[k], file=f)
    print('\n', file=f)
    print('行驶成本：%f \n' % obj1.getValue(), file=f)
    print('延迟成本：%f \n' % obj2.getValue(), file=f)
    print('总成本：%f \n' % obj.getValue(), file=f)
f.close()

pic = Draw(node_cor_x, node_cor_y, depot)
pic.construct_node_network(path)


