

def cal_service_time(set_N):
    """
    设定各节点的服务时间
    :param set_N:
    :return:
    """
    service_time = [0]  # 每个订单顾客节点的服务时间
    for j in set_N[1:-1]:
        service_time.append(2)
    service_time.append(0)
    return service_time


def cal_d_t_dc(orders, restaurants, set_P, set_N, depot, f_cost, speed):
    # 计算坐标和距离、时间、成本字典
    order_num = len(orders)
    start_node = 0
    dest_node = 2 * order_num + 1
    node_cor_x = {}  # 记录所有节点的横坐标
    node_cor_y = {}  # 记录所有节点的纵坐标
    node_cor_x[0] = depot[0]
    node_cor_x[2 * order_num + 1] = depot[1]
    node_cor_y[0] = depot[1]
    node_cor_y[2 * order_num + 1] = depot[1]
    for i in set_P:
        node_cor_x[i] = orders[i - 1].cor_x
        node_cor_y[i] = orders[i - 1].cor_y
        cur_res = restaurants[orders[i - 1].restaurant - 1]
        node_cor_x[i + order_num] = cur_res.cor_x
        node_cor_y[i + order_num] = cur_res.cor_y

    d_i_j = {}  # 记录各节点之间的距离
    t_i_j = {}  # 记录各节点之间的行驶时间
    dc_i_j = {}  # 记录各节点之间的行驶成本
    big_M = 100000
    for i in set_N:
        for j in set_N:
            d_i_j[i, j] = abs(node_cor_x[i] - node_cor_x[j]) + abs(node_cor_y[i] - node_cor_y[j])
            t_i_j[i, j] = d_i_j[i, j] / speed
            dc_i_j[i, j] = d_i_j[i, j] * f_cost
    d_i_j[start_node, dest_node] = big_M
    dc_i_j[start_node, dest_node] = big_M * f_cost
    t_i_j[start_node, dest_node] = d_i_j[start_node, dest_node] / speed
    d_i_j[dest_node, start_node] = big_M
    dc_i_j[dest_node, start_node] = big_M * f_cost
    t_i_j[dest_node, start_node] = d_i_j[dest_node, start_node] / speed
    return d_i_j, t_i_j, dc_i_j


def cal_q_j(set_P, set_D):
    q_j = [0]  # 记录各节点的取送餐情况
    for i in set_P:
        q_j.append(1)
    for i in set_D:
        q_j.append(1)
    q_j.append(0)
    return q_j
