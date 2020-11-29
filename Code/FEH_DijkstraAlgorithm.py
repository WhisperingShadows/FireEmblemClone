from typing import List


class Node:

    def __init__(self, data, indexloc=None):
        self.data = data
        self.index = indexloc
        self.holds = None


# to initialize graph normally, create nodes, instantiate graph object, and connect nodes
# Example:
# a = Node('a')
# g = Graph([a, b, c, d, e, f])
# g.connect(a, b, 5)
#
# to initialize graph as a grid use init_as_grid(width, length) method
# g = Graph.init_as_grid(3, 4)
class Graph:

    def __init__(self, nodes: List[Node], **kwargs):
        self.nodes = nodes
        if "adj_list" in kwargs:
            self.adj_list = kwargs["adj_list"]
        else:
            self.adj_list = [[node, []] for node in nodes]
        for i in range(len(nodes)):
            nodes[i].index = i

    def connect_dir(self, node1, node2, weight=1):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        # Note that the below doesn't protect from adding a connection twice
        self.adj_list[node1][1].append((node2, weight))

    def connect(self, node1, node2, weight=1):
        self.connect_dir(node1, node2, weight)
        self.connect_dir(node2, node1, weight)

    def connections(self, node):
        node = self.get_index_from_node(node)
        return self.adj_list[node][1]

    @staticmethod
    def get_index_from_node(node):
        if not isinstance(node, Node) and not isinstance(node, int):
            raise ValueError("Node must be an integer or a Node object")
        if isinstance(node, int):
            return node
        else:
            return node.index

    @staticmethod
    def create_grid(x, y, weight=1):
        nodes = []
        for y in range(1, y + 1):
            for x in range(1, x + 1):
                nodes.append(Node((x, y)))

        for i in range(len(nodes)):
            nodes[i].index = i

        adj_list = [[node, []] for node in nodes]

        for node_index in range(len(nodes)):
            adj_left = (node_index - 1 if node_index % x != 0 else None, weight)
            adj_right = (node_index + 1 if (node_index - x + 1) % x != 0 else None, weight)
            adj_up = (node_index + x if node_index + x <= nodes[-1].index else None, weight)
            adj_down = (node_index - x if node_index - x >= 0 else None, weight)
            for i in [adj_left, adj_right, adj_up, adj_down]:
                if i[0] is not None:
                    adj_list[node_index][1].append(i)
            # adj_list[node_index][1] = [adj_left, adj_right, adj_up, adj_down]

        return nodes, adj_list

    def get_grid_width_height(grid):
        return grid.adj_list[-1][0].data

    # xy and widthheight are both meant to be tuples
    def get_index_from_xy(self, xy):
        widthheight = self.get_grid_width_height()
        index = (xy[1] - 1) * widthheight[0] + xy[0] - 1
        if index < widthheight[0] * widthheight[1]:
            return index
        raise IndexError("Index of " + str(index) + " greater than " + str(
            widthheight[0] * widthheight[1]) + ", out of max range. Grid coordinate " + str(
            xy) + " was supplied, but the grid size was only " + str(widthheight))

    @classmethod
    def init_as_grid(cls, width, height):
        nodes, adj_list = cls.create_grid(width, height)
        graph = cls(nodes, adj_list=adj_list)
        return graph

    def dijkstra(self, src, endpoint=None, only_end=False, eval_to_length=-1):

        if isinstance(endpoint, tuple):
            endpoint = self.adj_list[self.get_index_from_xy(endpoint)][0]

        # check if endpoint is a possible destination node
        if endpoint and (endpoint not in [node_edges[0] for node_edges in self.adj_list]):
            print("Endpoint not in node list")
            return []

        # algorithm entry point
        if isinstance(src, tuple):
            src_index = self.get_index_from_xy(src)
        else:
            src_index = self.get_index_from_node(src)
        # Map nodes to DijkstraNodeDecorators
        # This will initialize all provisional distances to infinity
        dnodes = [DijkstraNodeDecorator(node_edges[0]) for node_edges in self.adj_list]
        # Set the source node provisional distance to 0 and its hops array to its node (itself)
        dnodes[src_index].prov_dist = 0
        dnodes[src_index].hops.append(dnodes[src_index].node)
        # Set up all heap customization methods
        is_less_than = lambda a, b: a.prov_dist < b.prov_dist
        get_index = lambda node: node.index()
        update_node = lambda node, data: node.update_data(data)

        # Instantiate heap to work with DijkstraNodeDecorators as the heap nodes
        heap = MinHeap(dnodes, is_less_than, get_index, update_node)

        min_dist_list = []

        min_decorated_node = type('obj', (object,), {'node': None})
        # while undiscovered nodes remain
        while heap.size() > 0 and not (min_decorated_node.node == endpoint and endpoint):
            # Get node in heap that has not yet been "seen"
            # that has smallest distance to starting node

            min_decorated_node = heap.pop()
            min_dist = min_decorated_node.prov_dist
            hops = min_decorated_node.hops
            if (not endpoint or (not only_end or min_decorated_node.node == endpoint)) and (
                    eval_to_length < 0 or (min_dist <= eval_to_length)):
                min_dist_list.append([min_dist, hops])

            # Get all next hops. This is no longer an O(n^2) operation
            # Now it's an O(log(n)) operation!
            connections = self.connections(min_decorated_node.node)
            # For each connection, update its path and total distance from
            # starting node if the total distance is less than the current distance
            # in dist array
            for (inode, weight) in connections:
                node = self.adj_list[inode][0]
                heap_location = heap.order_mapping[inode]
                if heap_location is not None:
                    tot_dist = weight + min_dist
                    if tot_dist < heap.nodes[heap_location].prov_dist:
                        hops_cpy = list(hops)
                        hops_cpy.append(node)
                        data = {'prov_dist': tot_dist, 'hops': hops_cpy}
                        heap.decrease_key(heap_location, data)

        return min_dist_list


class DijkstraNodeDecorator:

    def __init__(self, node):
        self.node = node
        self.prov_dist = float('inf')
        self.hops = []

    def index(self):
        return self.node.index

    def data(self):
        return self.node.data

    def update_data(self, data):
        self.prov_dist = data['prov_dist']
        self.hops = data['hops']
        return self


class BinaryTree:

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        self.nodes = nodes

    def root(self):
        return self.nodes[0]

    def iparent(self, i):
        return (i - 1) // 2

    def ileft(self, i):
        return 2 * i + 1

    def iright(self, i):
        return 2 * i + 2

    def left(self, i):
        return self.node_at_index(self.ileft(i))

    def right(self, i):
        return self.node_at_index(self.iright(i))

    def parent(self, i):
        return self.node_at_index(self.iparent(i))

    def node_at_index(self, i):
        return self.nodes[i]

    def size(self):
        return len(self.nodes)


class MinHeap(BinaryTree):

    def __init__(self, nodes, is_less_than=lambda a, b: a < b, get_index=None, update_node=lambda node, newval: newval):
        BinaryTree.__init__(self, nodes)
        self.order_mapping = list(range(len(nodes)))
        self.is_less_than, self.get_index, self.update_node = is_less_than, get_index, update_node
        self.min_heapify()

    # Heapify at a node assuming all subtrees are heapified
    def min_heapify_subtree(self, i):

        size = self.size()
        ileft = self.ileft(i)
        iright = self.iright(i)
        imin = i
        if ileft < size and self.is_less_than(self.nodes[ileft], self.nodes[imin]):
            imin = ileft
        if iright < size and self.is_less_than(self.nodes[iright], self.nodes[imin]):
            imin = iright
        if imin != i:
            self.nodes[i], self.nodes[imin] = self.nodes[imin], self.nodes[i]
            # If there is a lambda to get absolute index of a node
            # update your order_mapping array to indicate where that index lives
            # in the nodes array (so lookup by this index is O(1))
            if self.get_index is not None:
                self.order_mapping[self.get_index(self.nodes[imin])] = imin
                self.order_mapping[self.get_index(self.nodes[i])] = i
            self.min_heapify_subtree(imin)

    # Heapify an un-heapified array
    def min_heapify(self):
        for i in range(len(self.nodes), -1, -1):
            self.min_heapify_subtree(i)

    def min(self):
        return self.nodes[0]

    def pop(self):
        min_node = self.nodes[0]
        if self.size() > 1:
            self.nodes[0] = self.nodes[-1]
            self.nodes.pop()
            # Update order_mapping if applicable
            if self.get_index is not None:
                self.order_mapping[self.get_index(self.nodes[0])] = 0
            self.min_heapify_subtree(0)
        elif self.size() == 1:
            self.nodes.pop()
        else:
            return None
        # If self.get_index exists, update self.order_mapping to indicate
        # the node of this index is no longer in the heap
        if self.get_index is not None:
            # Set value in self.order_mapping to None to indicate it is not in the heap
            self.order_mapping[self.get_index(min_node)] = None
        return min_node

    # Update node value, bubble it up as necessary to maintain heap property
    def decrease_key(self, i, val):
        self.nodes[i] = self.update_node(self.nodes[i], val)
        iparent = self.iparent(i)
        while i != 0 and not self.is_less_than(self.nodes[iparent], self.nodes[i]):
            self.nodes[iparent], self.nodes[i] = self.nodes[i], self.nodes[iparent]
            # If there is a lambda to get absolute index of a node
            # update your order_mapping array to indicate where that index lives
            # in the nodes array (so lookup by this index is O(1))
            if self.get_index is not None:
                self.order_mapping[self.get_index(self.nodes[iparent])] = iparent
                self.order_mapping[self.get_index(self.nodes[i])] = i
            i = iparent
            iparent = self.iparent(i) if i > 0 else None

    def index_of_node_at(self, i):
        return self.get_index(self.nodes[i])

# a = Node('a')
# b = Node('b')
# c = Node('c')
# d = Node('d')
# e = Node('e')
# f = Node('f')

# g = Graph([a, b, c, d, e, f])

# g.connect(a, b, 5)
# g.connect(a, c, 10)
# g.connect(a, e, 2)
# g.connect(b, c, 2)
# g.connect(b, d, 4)
# g.connect(c, d, 7)
# g.connect(c, f, 10)
# g.connect(d, e, 3)

# g = Graph.init_as_grid(3, 4)

# print([i for i in g.get_grid_width_height()])

# for item in g.adj_list:
#     print(item[0].data, [g.adj_list[i[0]][0].data if i[0] is not None else None for i in item[1]])

# print([(weight, [n.data for n in node]) for (weight, node) in g.dijkstra(a)])
# from pprint import pprint
# pprint([(weight, [n.data for n in node]) for (weight, node) in g.dijkstra((1,1), (3,4), only_end=True)])
