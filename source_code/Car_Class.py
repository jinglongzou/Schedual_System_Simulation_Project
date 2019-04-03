#创建车辆类
from GlobalVar import Call_end_state_car_time,Call_wait_state_car_time,Call_start_car_time
from Map_Class_dict import Map
class car_class:
    '''
    attr:
        #基本信息
        baseinfo
        #时间管理
        init_time：
        final_time:
        #真实速度
        realspeed:
        #路径管理
        planpath: 车初始规划的路径，以列表形式存储的道路ID
        realpath：车实际走的路径
        #在道路上状态管理
        cur_roadID：车当前所在的道路
        end_distance: 车在当前道路上行驶了的距离
        turn_direction: 车将要转的方向：直行、左转、右转；这个参数是在到达路口时确定或者在进入路口时确定
        cur_state:车当前的状态
    method:
        1、规划路径
        2、状态修改：这是车辆的关键方法包括三种情况
                ①出发状态的更改：因为车辆对象创建后，并没有给以下变量赋值
                    (车辆的出发时间，计划路径，实际路径，车辆所在的道路，车辆距道路出口的长度，车辆状态，真实速度，方向）
                    在这里就要根据规划的路径和道路信息，给这些变量赋值。
                ②终止状态更改:
                    如果转变为等待态
                    如果仍然是终止态
                ③等待状态更改
                    如果入库
                    如果转变为终止态

        3、检查车辆能否走完当前道路
        4、检查当前路口是不是车辆的终点
        5、
        find_car_path:
        change_car_state:对不同的情境，做不同的状态修改
        update_car_time:

    '''
    def __init__(self,car):
        #car = [id,from,to,speed,planTime]
        self.baseinfo = car  # 车辆的基本信息

        self.start_time = None  # 车辆的实际出发时间
        #self.cur_time = None  # 车辆的当前时间
        self.final_time = None  # 车辆的到达时间

        self.realspeed = None  # 车辆的实际速度

        self.planpath = []  # 为车辆规划的路径，路径是道路ID
        self.cross_planpath = [] # 为车辆规划的路径，路径是路口ID
        #self.car_plan_crosspath = [] # 为车辆规划的路径,路径是路口节点
        self.realpath = []  # 车俩实际走过的路径，进入道路时，添加道路ID
        self.direction = -1 # 车辆在路口的行进方向，straight:-1;left:0;right:1;

        self.cur_road = None # 车当前所在的道路
        self.end_distance = None  # 车辆距离当前道路的出口距离
        # self.car_begin_distance = #车辆距离当前道路的入口距离
        self.cur_state =0 # 车辆的状态，wait_state：-1 ；end_state：1；在车库状态：0；
    #车辆出发函数
    #需要配置这些参数(车辆的出发时间，计划路径，实际路径，车辆所在的道路，车辆距道路出口的长度，车辆状态，真实速度，方向）
    def start_car(self, **kwargs):
        cur_time = kwargs['cur_time']
        cur_crossID = kwargs['cur_crossID']
        map_info = kwargs['map_info']
        schedual_system_info = kwargs['schedual_system_info']
        roadlist = kwargs['roadlist']
        crosslist = kwargs['crosslist']
       # 规划路径
        end_cross = self.baseinfo[2]
        self.plan_car_route(cur_crossID, end_cross, map_info, schedual_system_info)
        # 获取进入道路ID
        entry_roadID = self.planpath[0]
        # 获取目标道路对象
        entry_road = roadlist[entry_roadID]
        ## 检查目标道路是否允许车辆进入
        # 获取目标道路最后一个元素

        #选择要进入的目标道路的队列：

        last_elem = entry_road.last_car(cur_crossID)  # 可为：1 or [start_distance,laneID]
        if last_elem == -1:  # 当前道路已满
            # 不允许进图,此时应该重新规划路线，或者等待
            pass
        else:  # 目标道路存在车道有空位，允许进入目标道路，由于是出发，相当于直行，所以不存在冲突的问题，直接将车通过路口，并加入目标道路的队列
            #到前车的距离

            distance_tofrontcar = last_elem[0]
            entry_laneID = last_elem[1]
            # 赋值初始时间
            self.start_time = cur_time-1
            # 赋值车辆进入的道路
            self.cur_road = entry_roadID
            # 赋值真实路径
            self.realpath.append(self.cur_road)
            # 赋值车辆的速度
            entry_road_speed = entry_road.baseinfo[2] #进入道路限速
            self.realspeed = min(self.baseinfo[3], entry_road_speed, distance_tofrontcar)
            self.cur_state = 1  # 置为终止态
            ## 更改车距离道路出口的长度
            entry_road_length = entry_road.baseinfo[1]  #进入道路长度
            self.end_distance = entry_road_length - self.realspeed
            # 进入道路了，现在要先确定当前道路出口的转向
            ##################################################################
            # 获取当前道路的出口
            cur_road = roadlist[entry_roadID]
            cur_road_out_crossID = cur_road.find_cur_road_out_cross(cur_crossID)
            cur_road_out_cross = crosslist[cur_road_out_crossID]
            # 获取目标道路ID
            #target_roadID = self.find_target_roadID()
            # 获取目标道路对象
           # target_road = roadlist[target_roadID]
            ############################################################################
            # 设置当前车辆的转向
            self.set_car_direction( roadlist, crosslist, cur_crossID)
            #将车加入进入的道路的队列

            entry_road.enquene_car(self.baseinfo[0], self.end_distance, cur_crossID, entry_laneID) #[carID,end_distance,laneID]
            #将车弹出当前路口车库
            cur_cross = crosslist[cur_crossID]
            cur_cross.dequene_begin_carport()
            ############################################
            #输出某车，在t时刻进入道路的几车道
            print('{}号路口的{}号车，在{}时刻，进入{}号道路路的{}车道。 '.format(
                cur_crossID,self.baseinfo[0],self.start_time,entry_roadID,entry_laneID))
            Call_start_car_time.call_start_car_time += 1
            call_start_car_time = Call_start_car_time.call_start_car_time
            ###################################################






    #终止状态车辆状态更改函数,改变有两种可能性:一种改为等待态；二：仍是终止态；
    #终止状态车辆需要更改的参数：cur_time 或者car_end_distance
    def change_end_state_car(self,target_state,**kwargs):

        if target_state == -1:
            self.cur_state = -1 #置为等待态，不修改其他参数，有后面的等待态函数来处理
        else:
        #前一时刻为终止态，这一时刻仍然为终止态，需要修改参数：车辆距离出口的位置
            if kwargs:
                road_speed = kwargs['road_speed']
                distance_tofrontcar = kwargs['distance_tofrontcar']
                self.realspeed = min(self.baseinfo[3],road_speed,distance_tofrontcar)
                self.end_distance = self.end_distance - self.realspeed
            else:
                if self.end_distance < self.realspeed:
                    self.end_distance = 0
                else:
                    self.end_distance = self.end_distance - self.realspeed

        Call_end_state_car_time.call_end_state_car_num += 1
        call_end_state_car_num = Call_end_state_car_time.call_end_state_car_num

    #等待状态车辆的状态更改函数，改变有三种可能：一种回到车库；一种出路口改为终止态；一种为不出路口改为终止态；
    #等待状态车辆需要改变的参数：
    #   对回到车库：cur_state, end_distance, final_time
    #   对通过路口，改为终止态：real_speed, cur_road, end_distance, cur_state,
    #   对不同过路口，改为终止态
    def change_wait_state_car(self,**kwargs):
        '''
        以下参数在关键字参数kwargs中
        :param cur_time: 用于到达目的地的车辆，更新到达时间。
        :param target_state: 将要转变成的状态
        :param can_pass_cross: 是否能通过路口
        :param crossID: 当前路口ID,用于重新规划路径
        :param roadlist: 存储所有道路的字典
        :param distance_tofrontcar: 距离前车的距离，用于确定出发后的速度
        :param has_replanpath: 这是是否已经重新规划路径的标记，是一个布尔变量
        :return:
        '''
        target_state = kwargs['target_state']
        if target_state == 0: #入库
            cur_time=kwargs['cur_time']
            self.final_time = cur_time
            self.cur_state = 0

        else:#改为终止态
            can_pass_cross = kwargs['can_pass_cross']
            #不能通过路口需要修改参数：end_distance,cur_state
            if can_pass_cross is False: #不能通过路口，改为终止态
                road_speed = kwargs['road_speed']
                distance_tofrontcar = kwargs['distance_tofrontcar']
                self.realspeed = min(self.baseinfo[3],road_speed,distance_tofrontcar)
                self.end_distance = self.end_distance - self.realspeed
                self.cur_state = 1
            #能通过路口需要修改参数：cur_road，realpath，realspeed，end_distance，cur_state
            else:#能通过路口，改为终止态；
                target_road_speed = kwargs['target_road_speed']
                distance_tofrontcar = kwargs['distance_tofrontcar']
                target_roadID = kwargs['target_roadID']
                target_road_length = kwargs['target_road_length']
                # 赋值车辆进入的道路
                self.cur_road = target_roadID
                # 赋值真实路径
                self.realpath.append(self.cur_road)
                # 赋值车辆的速度
                self.realspeed = min(self.baseinfo[3], target_road_speed, distance_tofrontcar)
                # 通过路口后一定是终止态
                self.cur_state = 1  # 置为终止态
                # 更改车距离道路出口的长度
                self.end_distance = target_road_length - self.realspeed + self.end_distance
        Call_wait_state_car_time.call_wait_state_car_num +=1
        call_wait_state_car_num = Call_wait_state_car_time.call_wait_state_car_num
    #找到目标道路
    def find_target_roadID(self):
        '''
        :param has_replanpath: 这是是否重新规划路径的标记，是一个布尔变量
        :return:
                car_planpath = self.planpath
        if has_replanpath is True:
            return car_planpath[0]
        else:
        '''
        car_planpath = self.planpath
        cur_road = self.cur_road
        if self.cur_road is None:
            return car_planpath[0]
        else:
            n = len(car_planpath)
            for i in range(n):
                if car_planpath[i] == self.cur_road:
                    if i == n-1:
                        return -1
                    else:
                        return car_planpath[i + 1]
    #规划车辆的路径
    def plan_car_route(self,start_cross,end_cross,map_info,schedual_system_info):
        #根据车辆的起点、终点、地图信息、调度系统信息规划路径，返回一个起点到终点所经过的道路的路径，是以列表形式存储的；
        #首先计算出节点列表
        #在通过节点计算边路径
        #规划出路线后，首先检查下当前的道路是否是None: 是的话直接赋值给planpath；否则将当前道路放在新规划路径的最前面
        #规划出路径后，需要立即设置方向
        cross_path,road_path = map_info.find_shortest_path(start_cross,end_cross)
        self.planpath = road_path
        self.cross_planpath = cross_path
        pass
    #确定车辆的速度,车辆的速度是min(car_speed,road_speed,s)；distace_tofrontcar是到前车的距离
    def find_car_speed(self,roadspeed,distance_tofrontcar):
        return min(self.baseinfo[3],roadspeed,distance_tofrontcar)
    #确定车辆的转向,这需要根据当前道路和目标道路在路口中的关系来确定
    #规定直行为：-1;左转为：0;右转为1;
    def set_car_direction(self,roadlist,crosslist,crossID):
        # 获取当前道路的出口的基本信息
        cur_road = roadlist[self.cur_road]
        cur_road_out_crossID = cur_road.find_cur_road_out_cross(crossID)
        cur_road_out_cross_baseinfo = crosslist[cur_road_out_crossID].baseinfo
        # 获取目标道路ID
        target_roadID = self.find_target_roadID()
        if target_roadID == -1:
            return
        else:
            # 设置当前车辆的转向
            cur_roadID = self.cur_road
            planpath = self.planpath
            for i in range(4):
                if  cur_road_out_cross_baseinfo[i+1] == self.cur_road:
                    cur_road_index = i
                elif cur_road_out_cross_baseinfo[i+1] == target_roadID:
                    target_road_index = i

            if (cur_road_index + 2) % 4 == target_road_index:
                self.direction = -1 #直行
            elif (cur_road_index + 1) % 4 == target_road_index:
                self.direction = 0 #左转
            elif (cur_road_index + 3) % 4 == target_road_index:
                self.direction = 1 #右转
            else:
                return  'there somethin wrong! '
    #检车车辆能否走出当前路口
    def can_pass_road(self,**kwargs):
        if kwargs:
            target_road_speed = kwargs['target_road_speed']
            return self.realspeed > self.end_distance and self.end_distance < target_road_speed
        else:
            return self.realspeed > self.end_distance

    #检查当前路口是否是车辆的最终目的地
    def is_final_cross(self,crossID):
        return self.baseinfo[2] == crossID

    # 定义一个是否需要冲洗规划路径的检测函数
    def check_replanpath(self):
        pass

    def return_all_attr(self):
        attr = []
        attr.append({'baseinfo':self.baseinfo})
        attr.append({'cur_road':self.cur_road})
        attr.append({'end_distance': self.end_distance})
        attr.append({'realspeed': self.realspeed})
        attr.append({'direction': self.direction})
        attr.append({'cur_state': self.cur_state})
        attr.append({'planpath': self.planpath})
        return attr