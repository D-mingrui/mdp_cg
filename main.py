from gurobipy import *
from run_data import *
from utilities import *
from master_problem import MDP


if __name__ == '__main__':
    [orders, restaurants] = read_data(r'C:\Users\32684\Desktop\mdp_data\test\order1.txt',
                                      r'C:\Users\32684\Desktop\mdp_data\test\restaurant1.txt')
    order_num = len(orders)  # 订单的数量
    rider_num = 1  # 可用的骑手数量
    max_order = 5  # 每个骑手最多配送的订单数量
    speed = 400  # 骑手行驶的速度 米/分钟
    f_cost = 1  # 骑手行驶的单位距离成本
    depot = [1000, 1000]  # 配送中心的坐标

    set_P = [i for i in range(1, order_num + 1)]  # 集合P
    set_D = [i for i in range(order_num + 1, 2 * order_num + 1)]  # 集合D
    set_N = [i for i in range(2 * order_num + 2)]  # 集合N
    set_K = [k for k in range(rider_num)]
    # 各节点的服务时间
    service_time = cal_service_time(set_N)
    # 各节点的行驶距离字典、时间字典和行驶成本字典
    [d_i_j, t_i_j, dc_i_j] = cal_d_t_dc(orders, restaurants, set_P, set_N, depot, f_cost, speed)
    # 各节点的取货情况
    q_j = cal_q_j(set_P, set_D)

    mdp = MDP(rider_num, max_order, orders, restaurants, depot, d_i_j, dc_i_j, t_i_j, f_cost, service_time)
    mdp.init_model()
    obj, paths = mdp.solve()
    print(obj)
    for path in paths:
        print(path)


