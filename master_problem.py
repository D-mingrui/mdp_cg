from gurobipy import *
from run_data import *
import scipy.spatial.distance as sp


[orders, restaurants] = read_data(r'C:\Users\32684\Desktop\mdp_data\test\order1.txt',
                                  r'C:\Users\32684\Desktop\mdp_data\test\restaurant1.txt')
order_num = len(orders)     # 订单的数量
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
service_time = [0]    # 每个订单顾客节点的服务时间
for j in set_N[1:-1]:
    service_time.append(2)
service_time.append(0)

s_i = {}    # 餐馆i的单位延迟时间惩罚成本
l_i = {}    # 餐馆i的配送时效要求
B_i = {}    # 订单i的可取餐时间
depot = [6000, 6000]    # 配送中心的坐标
node_cor_x = {}     # 记录所有节点的横坐标
node_cor_y = {}     # 记录所有节点的纵坐标
node_cor_x[0] = depot[0]
node_cor_x[2 * order_num + 1] = depot[1]
node_cor_y[0] = depot[1]
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

class MDP:
    """
    外卖配送类，存储数据、模型和处理方法
    """
    def __init__(self, riders, capacity, orders, restaurants, d_i_j, t_i_j, ride_cost, service_time):
        """
        初始化数据
        :param riders: 骑手数量
        :param capacity: 每个骑手可配送的最大订单数
        :param orders: 订单集合
        :param restaurants: 餐馆集合
        :param d_i_j: 配送网络节点距离的字典
        :param t_i_j: 配送网络节点之间行驶时间的字典
        :param ride_cost: 骑手单位距离的骑行成本
        :param service_time: 在顾客节点的服务时间列表
        """
        order_num = len(orders)
        self.set_P = [i for i in range(1, order_num + 1)]  # 集合P
        self.set_D = [i for i in range(order_num + 1, 2 * order_num + 1)]  # 集合D
        self.set_N = [i for i in range(2 * order_num + 2)]  # 集合N
        self.set_K = [k for k in range(rider_num)]
        self.paths_orders = None    # 各路径对应的订单列表
        self.paths_cost = None  # 各路径的成本
        self.paths_time = None  # 各路径中到达各节点的时间
        self.paths_set = None
        self.paths = None   # 存储所有路径
        self.riders = riders    # 骑手数量
        self.capacity = capacity    # 每个骑手可配送的最大订单数
        self.orders = orders    # 订单集合
        self.restaurants = restaurants  # 餐馆集合
        self.node_num = len(orders) * 2 + 2    # 配送网络中的节点数
        self.nodes = [i for i in range(self.node_num)]  # 配送网络中的所有节点
        self.ready_time = [order.ready_time for order in orders]    # 所有订单的可取餐时间
        self.delivery_time = [restaurants[order.restaurant - 1].time for order in orders]   # 所有订单的要求配送时间
        self.penalty = [restaurants[order.restaurant - 1].penalty for order in orders]  # 所有订单的单位配送延迟成本
        self.dist = d_i_j   # 网络中各节点之间的距离
        self.travel_time = t_i_j    # 网络中各节点之间的行驶时间
        self.unit_ride_cost = ride_cost  # 骑手单位距离的骑行成本
        self.service_time = service_time    # 在顾客节点的服务时间

    def cal_path_time(self, path):
        """
        计算到达路径各节点的时间
        :param path: 路径的列表
        :return noe_time: 到达该路径各节点的时间
        """
        node_time = [0]
        for i in range(1, len(path)):
            arrive_time = node_time[i - 1] + self.travel_time[path[i - 1], path[i]]
            if path[i] > len(self.orders):  # 如果到达的是顾客节点，则顾客节点的离开时间等于到达时间加上服务时间
                node_time.append(arrive_time + self.service_time[path[i]])
            else:   # 如果到达的是商家节点，离开时间取”到达时间加上服务时间“和”可取餐时间“的最大值
                if arrive_time + self.service_time[path[i]] > self.ready_time[path[i]]:
                    node_time.append(arrive_time + self.service_time[path[i]])
                else:
                    node_time.append(self.ready_time[path[i]])
        return node_time

    def cal_path_cost(self, path, path_time):
        """
        输入路径和路径中到达各节点的时间，返回该路径的行驶成本和延迟成本之和
        :param path: 路径列表
        :param path_time: 节点到达时间列表
        :return: 路径的总成本
        """
        ride_cost = 0
        delay_cost = 0
        for i in range(len(path) - 1):
            ride_cost += self.dist[path[i], path[i + 1]] * self.unit_ride_cost
            if path[i] > len(self.orders):
                delay_time = 0
                order_index = path[i] - len(self.orders)
                if self.ready_time[order_index - 1] + self.delivery_time[order_index - 1] < path_time[i]:
                    delay_time = path_time[i] - (self.ready_time[order_index - 1] + self.delivery_time[order_index - 1])
                delay_cost += delay_time * self.penalty[order_index - 1]
        return ride_cost + delay_cost

    def initial_paths(self):
        """
        启发式方法得到初始解，返回初始解的路径和订单列表
        :return: 初始解路径列表，列表中的元素是每个路径的列表  以及  初始解订单列表
        """
        if self.riders * self.capacity < len(self.orders):
            return 'No Solution'
        ready_time_sorted_index = sorted(range(len(self.ready_time)), key=lambda i: self.ready_time[i]) # 对订单按取餐时间排序
        riders_orders = [[] for k in range(self.riders)]
        k_count = 0
        for index in ready_time_sorted_index:   # 分配订单
            while len(riders_orders[k_count % self.riders]) >= self.capacity:
                k_count += 1
            riders_orders[k_count % self.riders].append(index)
            k_count += 1
        riders_paths = [[0] for k in range(self.riders)]    # 根据分配的订单设定各骑手的行驶路径
        for k in range(self.riders):
            for order in riders_orders[k]:
                riders_paths[k].append(order + 1)
                riders_paths[k].append(order + 1 + len(self.orders))
        for k in range(self.riders):
            riders_paths[k].append(self.node_num)
        return riders_paths, riders_orders

    def init_model(self):
        """
        建立初始主问题模型
        """
        [self.paths, self.paths_orders] = self.initial_paths()
        self.paths_time = [self.cal_path_time(path) for path in self.paths]
        self.paths_set = set(self.paths)
        self.paths_cost = [self.cal_path_cost(self.paths[r], self.paths_time[r]) for r in range(len(self.paths))]

        model = Model('MDP')
        model.Params.OutputFlag = 0
        Y = []
        for r in range(len(self.paths)):
            name1 = 'y_' + str(r)
            Y.append(model.addVar(0, 1, vtype=GRB.CONTINUOUS, name=name1))
        obj = LinExpr(0)
        for r in range(len(self.paths)):
            obj.addTerms(self.paths_cost[r], Y[r])
        model.setObjective(obj, GRB.MINIMIZE)

        # 给a_i_r赋值
        a_i_r = {}
        for i in set_P:
            for r in range(len(self.paths)):
                a_i_r[i, r] = 0     # 初始化
        for r in range(len(self.paths)):
            for i in self.paths_orders[r]:
                a_i_r[i, r] = 1     # 赋值

        # constraint 30
        for i in self.set_P:
            expr = LinExpr(0)
            for r in range(len(self.paths)):
                expr.addTerms(a_i_r[i, r], Y[r])
            model.addConstr(expr == 1, 'c30')
            expr.clear()

        # constraint 31
        expr = LinExpr(0)
        for r in range(len(self.paths)):
            expr.addTerms(1, Y[r])
        model.addConstr(expr <= self.riders, 'c31')
        self.model = model

    def solve(self):
        """
        使用列生成方法求解MDP
        :return:
        """
















