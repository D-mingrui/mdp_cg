from gurobipy import *
from new_run_data import *
from utilities import *
from master_problem import MDP
import time


if __name__ == '__main__':
    origin_data_path = r'D:\资料\赵秋红导师组\本科毕设\文献\外卖配送\Li and Lim pdp_100\lc101.txt'
    depot_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\30_lc_101_depot.txt'
    pickup_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\30_lc_101_pickup.txt'
    delivery_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset\30_lc_101_delivery.txt'

    # [depot_node, pickup_nodes, delivery_nodes] = generate_read_data(origin_data_path)
    [depot_node, pickup_nodes, delivery_nodes] = read_data(depot_path, pickup_path, delivery_path)

    order_num = len(pickup_nodes)  # 订单的数量
    rider_num = 8  # 可用的骑手数量
    max_order = 5  # 每个骑手最多配送的订单数量
    speed = 2  # 骑手行驶的速度 米/分钟
    f_cost = 1  # 骑手行驶的单位距离成本
    depot = [depot_node.cor_x, depot_node.cor_y]  # 配送中心的坐标

    set_P = [i for i in range(1, order_num + 1)]  # 集合P
    set_D = [i for i in range(order_num + 1, 2 * order_num + 1)]  # 集合D
    set_N = [i for i in range(2 * order_num + 2)]  # 集合N
    set_K = [k for k in range(rider_num)]

    # 各节点的行驶距离字典、时间字典和行驶成本字典
    [d_i_j, t_i_j, dc_i_j] = cal_d_t_dc(pickup_nodes, delivery_nodes, set_P, set_N, depot, f_cost, speed)
    # 各节点的取货情况
    q_j = cal_q_j(set_P, set_D)
    start_time = time.time()
    mdp = MDP(rider_num, max_order, pickup_nodes, delivery_nodes, depot_node, d_i_j, dc_i_j, t_i_j, f_cost)
    mdp.init_model()
    obj, paths = mdp.solve()
    print(obj)
    for path in paths:
        print(path)
    end_time = time.time()
    print(end_time-start_time)

