from gurobipy import *
from run_data import *
from ESPPTWCPD import ESPPTWCPD, Node
import numpy as np


class MDP:
    """
    外卖配送类，存储数据、模型和处理方法
    """

    def __init__(self, riders, capacity, orders, restaurants, depot, d_i_j, dc_i_j, t_i_j, ride_cost, service_time):
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
        self.order_num = len(orders)
        self.set_P = [i for i in range(1, self.order_num + 1)]  # 集合P
        self.set_D = [i for i in range(self.order_num + 1, 2 * self.order_num + 1)]  # 集合D
        self.set_N = [i for i in range(2 * self.order_num + 2)]  # 集合N
        self.set_K = [k for k in range(riders)]
        self.paths_orders = None  # 各路径对应的订单列表
        self.paths_cost = None  # 各路径的成本
        self.paths_time = None  # 各路径中到达各节点的时间
        self.paths_set = None
        self.paths = None  # 存储所有路径
        self.riders = riders  # 骑手数量
        self.capacity = capacity  # 每个骑手可配送的最大订单数
        self.orders = orders  # 订单集合
        self.restaurants = restaurants  # 餐馆集合
        self.node_num = len(orders) * 2 + 2  # 配送网络中的节点数
        self.ready_time = [order.ready_time for order in orders]  # 所有订单的可取餐时间
        self.delivery_time = [restaurants[order.restaurant - 1].time for order in orders]  # 所有订单的要求配送时间
        self.penalty = [restaurants[order.restaurant - 1].penalty for order in orders]  # 所有订单的单位配送延迟成本
        self.dist = d_i_j  # 网络中各节点之间的距离
        self.dist_cost = dc_i_j  # 网络中各节点之间的行驶成本
        self.travel_time = t_i_j  # 网络中各节点之间的行驶时间
        self.unit_ride_cost = ride_cost  # 骑手单位距离的骑行成本
        self.service_time = service_time  # 在顾客节点的服务时间
        # 配送网络中的所有节点
        self.nodes = [Node(0, depot[0], depot[1])]
        for i in range(len(self.set_P)):
            self.nodes.append(Node(i + 1, restaurants[orders[i].restaurant - 1].cor_x,
                                   restaurants[orders[i].restaurant - 1].cor_y,
                                   delivery_time=restaurants[orders[i].restaurant - 1].time,
                                   penalty=restaurants[orders[i].restaurant - 1].penalty))
        for i in range(len(self.set_P)):
            self.nodes.append(Node(i + 1 + len(orders), orders[i].cor_x,
                                   orders[i].cor_y,
                                   restaurant=orders[i].restaurant,
                                   ready_time=orders[i].ready_time))
        self.nodes.append(Node(self.order_num * 2 + 1, depot[0], depot[1]))
        self.nodes[0].q_j = 0  # 起点节点不计入访问次数
        self.nodes[-1].q_j = 0  # 终点节点不计入访问次数

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
            else:  # 如果到达的是商家节点，离开时间取”到达时间加上服务时间“和”可取餐时间“的最大值
                if arrive_time + self.service_time[path[i]] > self.ready_time[path[i] - 1]:
                    node_time.append(arrive_time + self.service_time[path[i]])
                else:
                    node_time.append(self.ready_time[path[i] - 1])
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
        ready_time_sorted_index = sorted(range(len(self.ready_time)), key=lambda i: self.ready_time[i])  # 对订单按取餐时间排序
        riders_orders = [[] for k in range(self.riders)]
        k_count = 0
        for index in ready_time_sorted_index:  # 分配订单
            while len(riders_orders[k_count % self.riders]) >= self.capacity:
                k_count += 1
            riders_orders[k_count % self.riders].append(index)
            k_count += 1
        riders_paths = [[0] for k in range(self.riders)]  # 根据分配的订单设定各骑手的行驶路径
        for k in range(self.riders):
            for order in riders_orders[k]:
                riders_paths[k].append(order + 1)
                riders_paths[k].append(order + 1 + len(self.orders))
        for k in range(self.riders):
            riders_paths[k].append(0)
        return riders_paths, riders_orders

    def init_model(self):
        """
        建立初始主问题模型
        """
        [self.paths, self.paths_orders] = self.initial_paths()
        self.paths_time = [self.cal_path_time(path) for path in self.paths]
        self.paths_set = set()
        for path in self.paths:
            self.paths_set.add(tuple(path))
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
        for i in range(1, self.order_num + 1):
            for r in range(len(self.paths)):
                a_i_r[i, r] = 0  # 初始化
        for r in range(len(self.paths)):
            for i in self.paths_orders[r]:
                a_i_r[i + 1, r] = 1  # 赋值

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
        self.espptwcpd = ESPPTWCPD(self.capacity, self.nodes, self.dist_cost, self.travel_time, self.service_time)
        self.model.optimize()
        iter = 1
        print(iter)
        while self.model.status == GRB.OPTIMAL:
            duals = [constr.Pi for constr in self.model.getConstrs()]
            # duals = [100000 for constr in self.model.getConstrs()]
            self.espptwcpd.duals = duals
            labels = self.espptwcpd.solve()
            if labels and labels[0].cost - self.espptwcpd.duals[-1] > -0.001:
                return [self.model.getObjective().getValue(), self.used_path()]
            for label in labels:
                if label.cost - self.espptwcpd.duals[-1] > -0.001:
                    break
                path = [node.num for node in label.path]
                self.add_path(path, label.cost)
            self.model.optimize()
            iter += 1
            print(iter, labels[0].cost - self.espptwcpd.duals[-1])

    def add_path(self, path, reduced_cost):
        path_t = tuple(path)
        if path_t in self.paths_set:
            return

        self.paths.append(path_t)
        self.paths_set.add(path_t)

        coeffs = np.zeros(len(self.set_P) + 1)
        for i in path[1: -1]:
            if i <= self.order_num:
                coeffs[i - 1] = 1
        coeffs[-1] = 1
        cost = reduced_cost
        for i in path[1: -1]:
            if 1 <= i <= self.order_num:
                cost += self.espptwcpd.duals[i - 1]
        self.model.addVar(obj=cost, name=f"v{len(self.paths) - 1}",
                          column=Column(coeffs, self.model.getConstrs()))

    def used_path(self):
        return [(path, var.Obj, var.x)
                for path, var in zip(self.paths, self.model.getVars())
                if var.x != 0]
