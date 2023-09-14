import matplotlib.pyplot as plt


class Draw:
    def __init__(self, nodes_x, nodes_y, depot):
        self.nodes_x = nodes_x
        self.nodes_y = nodes_y
        self.depot = depot

    def construct_node_network(self, path):
        self.picture = plt.figure()
        for i in range(len(self.nodes_x)):
            plt.text(self.nodes_x[i], self.nodes_y[i], str(i), fontsize=15)
            if i == 0:
                plt.plot(self.nodes_x[i], self.nodes_y[i], 'o', color='red')
            elif i > int((len(self.nodes_x) - 2) / 2):
                plt.plot(self.nodes_x[i], self.nodes_y[i], 'o', color='black')
            else:
                plt.plot(self.nodes_x[i], self.nodes_y[i], 'o', color='brown')
        for k in range(len(path)):
            for i in range(len(path[k][0: -1])):
                start = (self.nodes_x[path[k][i]], self.nodes_x[path[k][i + 1]])
                end = (self.nodes_y[path[k][i]], self.nodes_y[path[k][i + 1]])
                plt.plot(start, end, color='blue')
        plt.show()






