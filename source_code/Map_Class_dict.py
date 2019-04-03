# 地图要由道路和路口来构建
# 输入：
#       道路：一个二维列表，road_list
#             备注：
#                   一条道路的信息：id,length,speed,channel,from,to,isDuplex
#       路口：一个二维列表，cross_list
#             备注：
#                   一个路口的信息：id,roadId,roadId,roadId,roadId
# 输出：
#       图：是一个对象


#创建邻接表的链节点
class GraghNode:
    def __init__(self):
        '''
        input:
            road_info: 指的是一条道路的信息数据
        attr:
            elem:是二维列表，每一行表示该节点沿一个方向的边信息；
                每一行（每一条边）中存储下一个节点编号、道路编号、道路长度、车道数、车道限速；
                每一行只记录出度，若沿某个方向的边，不存在从该节点出发的道路，则对应行为-1
        '''
        #节点的
        self.elem = []
    def append(self,data):
        self.elem.append(data)

import numpy as np
class Map:
    # 构建地图
    def __init__(self,roaddict,crossdict,direct_num = 4,unconn = 1000):
        '''
        :param roaddict: 所有道路对象构成的字典{roadID：road_class}
        :param crossdict: 所有路口对象构成的字典{roadID：road_class}
        :param direct_num:
        :param unconn:
        '''
        cross_num = len(crossdict)
        self._cross_num = cross_num
        self._unconn = unconn
        self.crossID_index = {}
        self.nvertex = None #记录路径
        self.adjMatrix = None #记录路径长度
        self._head = None
        i = 0
        for crossID in crossdict.keys():
            if crossID not in self.crossID_index.keys():
                self.crossID_index[crossID] = i
                i +=1
        if cross_num > 0:
            map_ =[None] *cross_num
            self._head = Map.create_map(self.crossID_index,map_,roaddict,crossdict)
        adjMatrix, nvertex = self.all_shortest_paths_floyd()
        self.nvertex =nvertex
        self.adjMatrix = adjMatrix
    @staticmethod
    def create_map(index,head, roaddict, crossdict):
        for cross in crossdict.values():
            crossID = cross[0]  # 获取当前节点ID
            #if crossID not in head.keys():
            crossID_index = index[crossID]
            head[crossID_index] = GraghNode()
            for roadID in cross[1:]:  # 依次获取该节点各个方向的边
                if roadID != -1:  # 当该方向存在边时
                    # 一条道路的信息：id, length, speed, channel,from, to, isDuplex
                    road = roaddict[roadID]  # 获取该方向的道路信息
                    # 当道路为双向车道时，或者道路为单向车道且从当前节点出发
                    if road[-3] == crossID:
                        # 下一个节点、道路编号、长度、限速、车道数、
                        next_crossID_index = index[road[-2]]
                        edge = [next_crossID_index, road[0], road[1], road[2], road[3]]
                        head[crossID_index].append(edge)
                    elif road[-1] == 1 and road[-2] == crossID:
                        next_crossID_index = index[road[-3]]
                        edge = [next_crossID_index, road[0], road[1], road[2], road[3]]
                        head[crossID_index].append(edge)
                    else:
                        head[crossID_index].append(-1)
                else:  # 当该方向不存在边时,就置为-1
                    head[crossID_index].append(-1)
            # print(head[cross_ID_minus].elem)
        return head

    def get_cross_num(self):
        return self.cross_num
    def get_head(self):
        return self._head
    def get_unconn(self):
        return self._unconn
    def is_empty(self):
        return  self._head is None
    #获取地图的任意两个节点之前的距离
    def get_edge(self,cross_i,cross_j):
        if cross_i == cross_j:
            return 0
        cross_i_index = self.crossID_index[cross_i]
        #print(cross_ID,self._head[cross_ID].elem)
        cross = self._head[cross_i_index].elem  #获取路口cross_i对应的各个方向的边
        for edge in cross:   # edge 为一条边:每一条边中存储下一个节点编号、道路编号、道路长度、车道数、车道限速；
            if edge == -1:
                continue
            else:
                cross_j_index = self.crossID_index[cross_j]
                if edge[0] == cross_j_index:
                    #cross_j_index = self.crossID_index[cross_j]
                    return edge[2]
        return self._unconn
    #获取地图任意两个节点之间的道路：
    def get_road_on_map(self,cross_i_index,cross_j_index):
        if cross_i_index == cross_j_index:
            return 'no road in same cross!' #这是输入错误的的情况，
        #print(cross_ID,self._head[cross_ID].elem)
        cross = self._head[cross_i_index].elem  #获取路口cross_i对应的各个方向的边
        for edge in cross:   # edge 为一条边:每一条边中存储下一个节点编号、道路编号、道路长度、车道数、车道限速；
            if edge == -1:
                continue
            else:
                if edge[0] == cross_j_index:
                    return edge
        return -1 #表明这两个加点不存在道路，路径规划错误
    #创建地图的邻接矩阵
    def build_adjMatrix(self):
        cross_num = self._cross_num
        adjMatrix = np.array([[self._unconn]*cross_num]*cross_num)
        for crossID_index in range(cross_num):
            #crossID_index = self.crossID_index[crossID]
            adjMatrix[crossID_index][crossID_index] = 0
            cross = self._head[crossID_index].elem
            for edge in cross:  # edge 为一条边:每一条边中存储下一个节点编号、道路编号、道路长度、车道数、车道限速；
                if edge == -1:
                    continue
                else:
                    next_crossID_index = edge[0]
                    adjMatrix[crossID_index][next_crossID_index] = edge[2]
        return adjMatrix
    def all_shortest_paths_floyd(self):
        cross_num = self._cross_num
        #邻接矩阵，也就是已知的最短路径长度
        adjMatrix = self.build_adjMatrix()
        #nvertex,记录已知最短路径的下一个节点
        nvertex = [[-1 if adjMatrix[i][i] == self._unconn else j for j in range(cross_num)] for i in range(cross_num)]

        for k in range(cross_num):
            for i in range(cross_num):
                for j in range(cross_num):
                    if adjMatrix[i][j] > adjMatrix[i][k] + adjMatrix[k][j]:
                        adjMatrix[i][j] = adjMatrix[i][k] + adjMatrix[k][j]
                        nvertex[i][j] = nvertex[i][k]
        return (adjMatrix,nvertex)
    def find_shortest_path(self,start_cross,end_cross):# 找到冲i到j的最短路径
        #查找出节点路径
        start = self.crossID_index[start_cross]
        end = self.crossID_index[end_cross]
        nvertex = self.nvertex
        cross_path = [start]
        prev = nvertex[start][end]
        while (prev != end):
            cross_path.append(prev)
            prev = nvertex[prev][end]
        cross_path.append(prev)
        #查找出道路路径
        road_path = []
        first = start
        for i in range(1,len(cross_path)):
            edge=self.get_road_on_map(first,cross_path[i])
            road_path.append(edge[1])
            first = cross_path[i]

        return  cross_path,road_path



