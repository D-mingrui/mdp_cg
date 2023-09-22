import random


class PickupNode:
    def __init__(self, num, cor_x, cor_y, demand, early_time, late_time, service_time, delivery_node_num):
        self.num = num
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.demand = demand
        self.early_time = early_time
        self.late_time = late_time
        self.service_time = service_time
        self.delivery_node_num = delivery_node_num
        self.q_j = 1


class DeliveryNode:
    def __init__(self, num, cor_x, cor_y, demand, early_time, late_time, service_time, pickup_node_num,
                 cost_time, restaurant, penalty):
        self.num = num
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.demand = demand
        self.early_time = early_time
        self.late_time = late_time
        self.service_time = service_time
        self.pickup_node_num = pickup_node_num
        self.cost_time = cost_time
        self.restaurant = restaurant
        self.penalty = penalty
        self.q_j = 1


class DepotNode:
    def __init__(self, num, cor_x, cor_y, early_time, late_time):
        self.num = num
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.early_time = early_time
        self.late_time = late_time
        self.q_j = 0
        self.service_time = 0


def generate_read_data(data_path):
    """
    num0	X1	Y2	demand3	early_time4	late_time5	service_time6	pickup7	delivery8
    :param data_path: 读取文件路径
    :return: depot, pickup nodes, delivery nodes
    """
    request_num = 30
    with open(data_path) as origin_data_file:
        lines = origin_data_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:]]
        depot = DepotNode(0, data[0][1], data[0][2], data[0][4], data[0][5])
        requests = data[1:]
        random.shuffle(requests)  # 随机打乱数据的顺序
        pickup_nodes = []
        delivery_nodes = []
        num = 1
        for line in requests:
            if line[8] > 0:
                pickup_nodes.append(PickupNode(num, line[1], line[2], line[3], line[4], line[5], line[6], line[8]))
                # 寻找对应的送餐节点
                for line_inner in data:
                    if line_inner[0] == line[8]:
                        # 计算成本的最晚时间和右时间窗一致，所属餐馆和惩罚成本暂时都设为0
                        delivery_nodes.append(DeliveryNode(num + request_num, line_inner[1], line_inner[2], line_inner[3],
                                                           line_inner[4], line_inner[5], line_inner[6], line_inner[7],
                                                           line_inner[5], 0, 0))
                        break
                num += 1
                if len(pickup_nodes) == request_num:  # 随机取出data_size对取送货节点
                    break

    folder_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset'
    depot_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset' + '//' + str(request_num) + '_lc_101_depot' + '.txt'
    pickup_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset' + '//' + str(request_num) + '_lc_101_pickup' + '.txt'
    delivery_path = r'C:\Users\32684\Desktop\mdp_data\LL_dataset' + '//' + str(request_num) + '_lc_101_delivery' \
                    + '.txt'
    with open(depot_path, 'w') as depot_file:
        print('num', 'X', 'Y', 'e', 'l', sep='\t', file=depot_file)
        print(depot.num, depot.cor_x, depot.cor_y, depot.early_time, depot.late_time, sep='\t', file=depot_file)
    with open(pickup_path, 'w') as pickup_file:
        print('num', 'X', 'Y', 'demand', 'e', 'l', 'service_time', 'delivery', sep='\t', file=pickup_file)
        for pickup_node in pickup_nodes:
            print(pickup_node.num, pickup_node.cor_x, pickup_node.cor_y, pickup_node.demand,
                  pickup_node.early_time, pickup_node.late_time, pickup_node.service_time,
                  pickup_node.delivery_node_num, sep='\t', file=pickup_file)
    with open(delivery_path, 'w') as delivery_file:
        print('num', 'X', 'Y', 'demand', 'e', 'l', 'service_time', 'pickup', 'cost_time', 'restaurant',
              'penalty', sep='\t', file=delivery_file)
        for delivery_node in delivery_nodes:
            print(delivery_node.num, delivery_node.cor_x, delivery_node.cor_y, delivery_node.demand,
                  delivery_node.early_time, delivery_node.late_time, delivery_node.service_time,
                  delivery_node.pickup_node_num, delivery_node.cost_time, delivery_node.restaurant,
                  delivery_node.penalty, sep='\t', file=delivery_file)

    return depot, pickup_nodes, delivery_nodes


def read_data(depot_path, pickup_path, delivery_path):
    with open(depot_path) as depot_file:
        lines = depot_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:]]
        depot = DepotNode(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4])
    with open(pickup_path) as pickup_file:
        lines = pickup_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:]]
        pickup_nodes = [PickupNode(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7])
                        for line in data]
    with open(delivery_path) as delivery_file:
        lines = delivery_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:]]
        delivery_nodes = [DeliveryNode(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7],
                                       line[8], line[9], line[10])
                          for line in data]
    return depot, pickup_nodes, delivery_nodes
