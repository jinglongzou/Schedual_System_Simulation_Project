#道路类
#这是基于列表来实现道路的车辆管理队列,因此有以下两个问题：
# 第一个元素的弹出复杂度是O(n)，
# 由于是列表没有确定长度,因此其会动态扩展列表容量，也就是会重新分配存储区，并复制现有的数据
class RoadQueneError(Exception):
    pass
from operator import itemgetter
class road_class:
    #roadlist = [id,length,speed,channel,from,to,isDuplex]
    def __init__(self,road):
        '''
        attr:
            baseinfo:
            from_to_queues:这是一个二维数组，有几个车道，就有几行；每一行存储该车道的所有车辆；每一行的元素存储[车辆ID,距道路出口长度]
            to_from_queues:
            #定义一个标记，表示当前道路没有车辆可以通过路口:
        method:
            yield_car: 1、遍历，修改每一辆车，用于道路上车辆的,终止态修改函数
            first_car: 2、访问最优先的车辆，用于出路口
            dequene: 3、弹出最优先的车辆，用于弹出出路口的车
            last_car: 4、访问对低优先级的车辆，用于判断目标道路是否允许车辆加入
            enquene: 5、车辆入队
            check_road: 6、检查当前道路是否还有车辆可以通过道路,这个方法可以通过first_car来实现
                            如果返回-1,表明道路上没有车了。如果返回车了，检查车辆是否为终止态，是的话：表明没有车可以
                            出路口了；不是：表明还有车辆可以出路口，或者还有车辆没有更新状态，出错了。
        '''
        self.baseinfo = road
        self.from_to_quene = []
        self.to_from_quene = []
        #构建道路上车辆的存储队列
        # roadlist = [id,length,speed,channel,from,to,isDuplex]
        if self.baseinfo[-1] == 0:
            for i in range(self.baseinfo[3]):
                self.from_to_quene.append([])
        else:
            for i in range(self.baseinfo[3]):
                self.from_to_quene.append([])
                self.to_from_quene.append([])

    #根据路口ID返回当前道路的队列
    def return_road_quene(self,crossID):
        if crossID == self.baseinfo[5]:
            return self.from_to_quene
        else:
            return self.to_from_quene
    #将一辆车加入队列：每一个元素是[carID,end_distance,cur_crossID,laneID]
    def enquene_car(self,carID, end_distance, cur_crossID, laneID):
        if cur_crossID == self.baseinfo[5]:
            next_crossID = self.baseinfo[4]
        else:
            next_crossID = self.baseinfo[5]
        quenelist = self.return_road_quene(next_crossID)
        quenelist[laneID].append([carID, end_distance,laneID]) #加入队列
        #quenelist.sort(key=itemgetter(1,2),reverse=True) #排序队列
    #弹出队列的一辆车：
    def dequene_car(self,crossID,laneID):
        quenelist = self.return_road_quene(crossID)
        if quenelist == []:
            return -1 #队列为空
        else:
            return quenelist[laneID].pop(0)
     #按照优先级排序的车辆
    def sorted_quene(self,crossID):
        quenelist = self.return_road_quene(crossID)
        temp = []
        for i in range(len(quenelist)):
            temp = temp + quenelist[i]
        temp.sort(key=itemgetter(1,2))
        return temp
    #
    # 根据选择的方向，输出道路上的所有车辆,这里根据道路上的车辆队列，创建一个生成器函数
    # 遍历道路上的每一辆车
    def yield_car(self, crossID):  # 根据道路的终点路口ID来确定选择的道路方向
        quenelist = self.return_road_quene(crossID)
        #遍历道路上每一个车道上的车
        channel_num = self.baseinfo[3]
        for i in range(channel_num):
            #对每一条车道上的车进行访问
            for elem in quenelist[i]:
                yield [elem[0],elem[1],i] #生成[carID,end_distance,laneID]
    #访问道路上往当前路口行驶的最高优先级的车辆：道路上有车辆就返回：队列元素；道路上没有车辆就返回：-1
    def first_car(self,crossID):
        quenelist = self.return_road_quene(crossID)
        channel_num = self.baseinfo[3]
        min = [-1,float('inf')]
        for i in range(channel_num):
            if quenelist[i] !=[]: #如果第i个车道上有车辆
                if min[-1] > quenelist[i][0][1]: #比较距道路出口的长度
                    min = [i,quenelist[i][0][1]]
        if min[0] != -1:
            #carID = quenelist[min[0]][0][0]
            #end_distance = quenelist[min[0]][0][1]
            return quenelist[min[0]][0]#[carID,end_distance,i] #[carID,distance_end,laneID]
        else:
            return -1 #表明当前道路上没有车辆
    #访问道路上往当前路口行驶的,每个车道最后的一辆车
    def last_car(self,crossID):  #返回值：可为：1 or [-1,laneID] or [0,carID,end_distance,laneID]
        if crossID == self.baseinfo[5]:
            next_crossID = self.baseinfo[4]
        else:
            next_crossID = self.baseinfo[5]
        quenelist = self.return_road_quene(next_crossID)
        channel_num = len(quenelist)
        for i in range(channel_num):
            if quenelist[i] !=[]: #如果第i个车道上有车辆
                last = quenelist[i][-1] #访问该车道最后一辆车
                #比较车尾距道路入口的距离
                start_distance = self.baseinfo[1] - last[1] -1 #车尾距道路入口的距离
                if start_distance > 0:
                    return [start_distance,i,last[0]] # [start_distance,laneID]   #x返回[当前车道有车标记，carID,start_distance,laneID]
                else:
                    continue
            else:
                return [self.baseinfo[1],i,1] #返回[start_distance,laneID,1] #表示道路为空
        return -1 #表明当前道路，已经满了，不允许进入车辆
    #检查存储开往当前路口车辆的队列是否为空
    def road_quene_isempty(self,crossID):
        quenelist = self.return_road_quene(crossID)
        for i in range(len(quenelist)):
            if quenelist[i] !=[]:
                return False
        return True
    def find_cur_road_out_cross(self,crossID):
        if self.baseinfo[-1] == 0:
            return self.baseinfo[-2]
        else:
            if self.baseinfo[-2] == crossID:
                return self.baseinfo[-3]
            else:
                return self.baseinfo[-2]
    #更改道路队列中的元素的到终点的距离
    def change_end_ditance_in_quene(self,crossID,cur_carID,cur_car_laneID,end_distance):
        quenelist = self.return_road_quene(crossID)
        for elem in quenelist[cur_car_laneID]:
            if elem[0] == cur_carID:
                elem[1] = end_distance
                break