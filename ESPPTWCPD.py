from collections import deque
from functools import lru_cache
from copy import deepcopy


class Node:
    def __init__(self, node_num, cor_x, cor_y, restaurant=None, ready_time=None, delivery_time=None, penalty=None):
        self.num = node_num
        self.q_j = 1
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.restaurant = restaurant
        self.ready_time = ready_time
        self.delivery_time = delivery_time
        self.penalty = penalty


class Label:
    def __init__(self, node, cost, order_num, time, unreachable_orders: set, current_orders: set, prev=None):
        self.node = node
        self.cost = cost
        self.load = order_num
        self.time = time
        self.U = unreachable_orders
        self.W = current_orders
        self.prev = prev
        self.dominated = False

    @property
    @lru_cache(maxsize=1)
    def path(self):
        label = self
        path = []
        while label.prev:
            path.append(label.node)
            label = label.prev
        path.append(label.node)
        return list(reversed(path))

    def dominates(self, label):
        """
        如果本标签占优输入的标签，则返回True，否则返回false
        """
        if self.cost <= label.cost and self.load <= label.load and self.time <= label.time \
                and self.U.issubset(label.U) and self.W.issubset(label.W):
            flag = True
        else:
            flag = False
        return flag

    def is_dominated(self):
        for label in self.node.labels:
            if label.dominates(self):
                return True
        return False

    def filter_dominated(self):
        labels = []
        for label in self.node.labels:
            if self.dominates(label):
                label.dominated = True
            else:
                labels.append(label)
        self.node.labels = labels


class ESPPTWCPD:
    """
    nodes是Node实例列表，共有订单数乘2加1个元素；
    capacity是每个骑手最多配送的订单数
    """
    def __init__(self, capacity, nodes, dc_i_j: dict, t_i_j: dict, service_time):
        self.capacity = capacity
        self.nodes = nodes
        self.orders_num = int((len(nodes) - 1) / 2)
        self.duals = []
        self.depot_node = nodes[0]
        self.ready_time = [node.ready_time for node in self.nodes[(self.orders_num + 1):]]
        self.delivery_time = [node.delivery_time for node in self.nodes[1: (self.orders_num + 1)]]
        self.penalty = [node.penalty for node in self.nodes[1: (self.orders_num + 1)]]
        self.dist_cost = dc_i_j  # 网络中各节点之间的距离
        self.travel_time = t_i_j  # 网络中各节点之间的行驶时间
        self.service_time = service_time    # 节点的服务时间

    def solve(self):
        for node in self.nodes:
            node.labels = []
        to_be_extended = deque([self.depot_label()])
        while to_be_extended:
            from_label = to_be_extended.popleft()
            if from_label.dominated:
                continue

            to_labels = self.feasible_label_from(from_label)
            for to_label in to_labels:
                to_node = to_label.node
                if to_node is not self.depot_node:
                    if to_label.is_dominated():
                        continue
                    to_label.filter_dominated()
                    to_be_extended.append(to_label)
                to_node.labels.append(to_label)

        return sorted(self.depot_node.labels, key=lambda x: x.cost)

    def depot_label(self):
        # U = [node for node in self.nodes[(self.orders_num + 1):]]
        U = set()
        W = set()
        return Label(self.depot_node, 0, 0, 0, U, W)

    def feasible_label_from(self, from_label: Label):
        to_labels = []
        for to_node in (set(self.nodes[1: self.orders_num + 1]) - from_label.U):
            to_label = self.extended_label(from_label, to_node)
            if not to_label:
                from_label.U.add(to_node)
            else:
                to_labels.append(to_label)
        for unfinished_node in from_label.W:
            to_label = self.extended_label(from_label, self.nodes[unfinished_node.num + self.orders_num])
            to_labels.append(to_label)
        to_labels.append(self.extended_label(from_label, self.depot_node))

        return to_labels

    def extended_label(self, from_label: Label, to_node: Node):
        # 计算下一个节点的订单量
        load = from_label.load + to_node.q_j
        if load > self.capacity:
            return

        # 计算下一个节点的时间
        from_node = from_label.node
        if to_node.num > self.orders_num:   # 下一个节点是顾客节点
            time = from_label.time + self.travel_time[from_node.num, to_node.num] + self.service_time[to_node.num]
        else:   # 下一个节点是商家节点
            time = max(from_label.time + self.travel_time[from_node.num, to_node.num] + self.service_time[to_node.num],
                       self.ready_time[to_node.num - 1])

        # 计算下一个节点的成本
        ride_cost = self.dist_cost[from_node.num, to_node.num]
        delay_cost = 0
        dual_cost = 0
        if to_node.num > self.orders_num:   # 下一个节点是顾客节点
            delay_time = max(0, time - to_node.ready_time - self.delivery_time[to_node.restaurant - 1])
            delay_cost = delay_time * self.penalty[to_node.restaurant - 1]
        if 1 <= from_node.num <= self.orders_num:     # 下一个节点是商家节点
            dual_cost += self.duals[from_node.num - 1]
        cost = ride_cost + delay_cost - dual_cost

        # 计算下一个节点的W
        # 计算下一个节点的U
        W = set()    # 已经开始服务但尚未完成的订单集合
        for node in list(from_label.W):
            W.add(node)
        U = set()    # 不可访问的订单
        for node in list(from_label.U):
            U.add(node)
        if to_node.num > self.orders_num:  # 如果下一个节点是顾客节点
            W.remove(self.nodes[to_node.num - self.orders_num])
        else:  # 如果下一个节点是商家节点
            W.add(to_node)
            U.add(to_node)

        return Label(to_node, cost, load, time, U, W, from_label)













