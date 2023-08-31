
class Order:
    def __init__(self, num, cor_x, cor_y, restaurant, ready_time):
        self.num = num
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.restaurant = restaurant
        self.ready_time = ready_time


class Restaurant:
    def __init__(self, num, cor_x, cor_y, time, penalty):
        self.num = num
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.time = time
        self.penalty = penalty


def read_data(order_path, res_path):
    with open(order_path) as order_file:
        lines = order_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:6]]
        orders = [Order(line[0], line[1], line[2], line[3], line[4]) for line in data if line]
    with open(res_path) as res_file:
        lines = res_file.readlines()
        data = [[int(i) for i in line.split()] for line in lines[1:]]
        restaurants = [Restaurant(line[0], line[1], line[2], line[3], line[4]) for line in data if line]
    return orders, restaurants









