#路口类
#路口的两个车库管理，要求对未出发的车库要求，车辆按照出发时间、车辆ID排序
from GlobalVar import Call_end_state_car_time,Call_wait_state_car_time,Cur_Time,End_carport_car_num
class cross_class:
    #crosslist = [id,roadId,roadId,roadId,roadId]
    def __init__(self,crosslist):
        '''
        attr:
            #路口基本信息
            baseinfo
            #路口管理信息
            begin_gabage: #存未到既定出发时间的车辆
            end_gabage: #存到达目的地的车辆
        method:
            1、将未出发的车辆加入未出发车库
            2、访问未出发车库的第一优先级车辆
            3、弹出未出发车库第一优先级车辆
            4、将到达最终目的地的车辆加入终点库
            5、针对某条道路某个转向的车，检测可能冲突的道路
            6、检测对一辆车是否有冲突
        '''
        self.baseinfo = crosslist
        # 存未出发的车辆，这个结构中存储的元素是先按照plantime排序从大到小，再按照carID排序从大到小,
        self.begin_carport = []  #每一个元素是[plantime,carID]
        self.end_carport = [] #存到达目的地的车辆 ,直接用列表存储
    #初始，将车辆加入路口的‘未出发车库’
    def enquene_begin_carport(self,elem):
        '''
        :param elem: [plantime,carID]
        排序复杂度分析：每次插入最多遍历整个列表，也就是O(n)；列表的插入时间复杂度为O(n)；
        因此本入队算法的时间复杂度为O(n^2)
        :return:
        '''
        begin_carport = self.begin_carport
        n = len(begin_carport)
        for i in range(n):
            if begin_carport[i][0] <= elem[0]:
                if begin_carport[i][0] < elem[0]:
                    begin_carport.insert(i, elem)
                    return
                elif begin_carport[i][0] == elem[0]:
                    for j in range(i, n):
                        if begin_carport[j][0] == elem[0] and begin_carport[j][1] < elem[1]:
                            begin_carport.insert(j, elem)
                            return
                        elif begin_carport[j][0] < elem[0]:
                            begin_carport.insert(j, elem)
                            return
                else:
                    break
        begin_carport.append(elem)
        return

    #弹出未出发的车辆
    def dequene_begin_carport(self):
        if self.begin_carport == []:
            return -1
        else:
            return self.begin_carport.pop(-1)
    #访问未出发车库第一优先级元素
    def peek_begin_carport(self):
        if self.begin_carport == []:
            return -1
        else:
            return self.begin_carport[-1]
    #将到达目的的车辆加入‘到达目的地车库’
    def enquene_end_carport(self,carID):
        self.end_carport.append(carID)
    #检查当前路口是否有车辆冲突,返回可能冲突的道路,#规定直行为：-1;左转为：0;右转为1;
    def find_maybe_conflict_roadID(self,cur_car): #roadlist是道路对象的集合，cur_car是当前的道路对象
        cur_roadID = cur_car.cur_road
        for i in range(4):
            if self.baseinfo[i+1] == cur_roadID: #
                if cur_car.direction == 0:
                    conflict_road_index = (i + 3) % 4 + 1
                    return self.baseinfo[conflict_road_index] #若返回的道路ID是-1,表明没有冲突
                elif cur_car.direction == 1:
                    conflict_road_index_S = (i + 1) % 4 + 1 #可能的：与直行道路冲突
                    conflict_road_index_L = (i + 2) % 4 + 1 #可能的：与左转道路冲突
                    return [self.baseinfo[conflict_road_index_S], self.baseinfo[conflict_road_index_L]]#若返回的道路ID是-1,表明没有冲突
                else:#当前车辆直行，不会有冲突
                    return -1 #表示没有冲突
        else:
            return -1
    #检查当前车辆是否在本路口冲突，返回一个布尔值
    def check_if_conflict(self,roadlist, carlist, cur_car):
        maybe_conflict_roadID = self.find_maybe_conflict_roadID(cur_car)
        crossID = self.baseinfo[0]
        exist_conflict = False # 用来统一冲突问题
        if maybe_conflict_roadID == -1:  # 直行没有冲突或者冲突的道路不存在
            pass  # 没有冲突
        else:  # 存在冲突的道路
            if isinstance(maybe_conflict_roadID, list):  # 当前车为右转时，可能冲突的有两种类型的道路
                maybe_conflict_roadID_S = maybe_conflict_roadID[0]
                maybe_conflict_roadID_L = maybe_conflict_roadID[1]
                if maybe_conflict_roadID_S != -1:
                    maybe_conflict_road = roadlist[maybe_conflict_roadID_S]
                    if maybe_conflict_road.baseinfo[-1] ==0 and crossID != maybe_conflict_road.baseinfo[5]:
                        pass
                    else:
                        conflict_first_elem = maybe_conflict_road.first_car(crossID)
                        if conflict_first_elem == -1:
                            # 冲突道路没有车，可以进入目标道路
                            pass
                        else:
                            # 找到可能冲突的车了
                            maybe_conflict_carID = conflict_first_elem[0]
                            maybe_conflict_car = carlist[maybe_conflict_carID]
                            if maybe_conflict_car.cur_state == -1 and maybe_conflict_car.direction == -1:
                                # 冲突了,跳出当前道路
                                exist_conflict = True
                            else:  # 不冲突
                                pass
                elif maybe_conflict_roadID_L != -1:
                    maybe_conflict_road = roadlist[maybe_conflict_roadID_L]
                    if maybe_conflict_road.baseinfo[-1] ==0 and crossID != maybe_conflict_road.baseinfo[5]:
                        pass
                    else:
                        conflict_first_elem = maybe_conflict_road.first_car(crossID)
                        if conflict_first_elem == -1:
                            # 冲突道路没有车，可以进入目标道路
                            pass
                        else:
                            # 找到可能冲突的车了
                            maybe_conflict_carID = conflict_first_elem[0]
                            maybe_conflict_car = carlist[maybe_conflict_carID]
                            if maybe_conflict_car.cur_state == -1 and maybe_conflict_car.direction == 0:
                                # 冲突了,跳出当前道路
                                exist_conflict = True
                            else:  # 不冲突
                                pass
            else:  # 当前车左转，检查是否冲突
                maybe_conflict_road = roadlist[maybe_conflict_roadID]
                if maybe_conflict_road.baseinfo[-1] == 0 and crossID != maybe_conflict_road.baseinfo[5]:
                    pass
                else:
                    conflict_first_elem = maybe_conflict_road.first_car(crossID)
                    if conflict_first_elem == -1:
                        # 冲突道路没有车，可以进入目标道路
                        pass
                    else:
                        # 找到可能冲突的车了
                        maybe_conflict_carID = conflict_first_elem[0]
                        maybe_conflict_car = carlist[maybe_conflict_carID]
                        if maybe_conflict_car.cur_state == -1 and maybe_conflict_car.direction == -1:
                            # 冲突了,跳出当前道路
                            exist_conflict = True
                        else:  # 不冲突
                            pass
        return exist_conflict
    #检查当前路口是否还有车能通过路口，返回布尔值
    def check_has_car_can_pass(self,roadlist,carlist):
        cross_baseinfo = self.baseinfo
        crossID = cross_baseinfo[0]
        for roadID in cross_baseinfo[1:]:
            if roadID == -1:
                continue
            else:
                road = roadlist[roadID]
                if road.baseinfo[-1] == 0 and road.baseinfo[5] != self.baseinfo[0]:
                    continue
                first_elem = road.first_car(crossID)
                if first_elem == -1:
                    continue
                else:
                    carID = first_elem[0]
                    car = carlist[carID]
                    if car.cur_state == -1:
                        return True
        return False
    #车辆在当前路口出发
    def start_car_on_cross(self,cur_time,roadlist, carlist,map_info,schedual_system_info,crosslist):
        cur_crossID = self.baseinfo[0]
        n = len(self.begin_carport)
        for i in range(n-1,-1,-1):
            elem = self.begin_carport[i]
            plantime = elem[0]
            cur_carID = elem[1]
            if plantime < cur_time:  # 理论上车库中车的计划时间小于当前时间的都可以出发
                cur_car = carlist[cur_carID]
                cur_car.start_car(cur_time =cur_time,cur_crossID = cur_crossID,
                                    map_info = map_info,
                                    schedual_system_info = schedual_system_info,
                                    roadlist = roadlist,
                                    crosslist = crosslist
                                  )
            else:
                break

    #路口终止状态车辆的处理函数
    def end_state_car_function(self,cur_time,roadlist,carlist):
        cross_baseinfo = self.baseinfo  # 路口基本信息
        crossID = cross_baseinfo[0]
        for roadID in cross_baseinfo[1:]:  # 对当前路口的每一条道路
            if roadID == -1:
                continue
            else:
                # 备注：这里不需要在区分是单向道路还是双向道路，因为通过传入当前的crossID,
                #      可以直接在road对象内选择存储开往当前路口的队列
                road = roadlist[roadID]  # 获取道路对象
                road_baseinfo = road.baseinfo  # 获取道路的基本信息
                # 需要判断当前路口是否是当前道路的出口
                if road_baseinfo[-1] == 0:
                    if crossID != road_baseinfo[-2]:
                        continue

                if road.road_quene_isempty(crossID) is True:  # 当前道路存储开往当前路口的队列为空
                    continue
                else:  # 当前道路存储开往当前路口的队列不为空
                    pre_car_quene = [None]*road.baseinfo[3]  # 当前道路的前车，[pre_carID,laneID] 也就是前车ID、前车所在的车道
                    for elem in road.yield_car(crossID):  # 开始遍历当前道路的每一辆车elem = [carID,end_distance,laneID]
                        cur_carID = elem[0]  # 当前车的ID
                        cur_car_end_distance = elem[1]  # 车距离道路出口车距离
                        cur_car_laneID = elem[2]  # 当前车所在的车道
                        cur_car = carlist[cur_carID]  # 当前车辆对象
                        if cur_car.cur_state == -1:  # 如果车辆的状态是等待态，就跳过
                            continue
                        else:
                            can_pass_road_flag = True
                            target_roadID = cur_car.find_target_roadID()
                            if target_roadID == -1:
                                can_pass_road_flag = cur_car.can_pass_road()
                            else:
                                target_road = roadlist[target_roadID]
                                target_road_speed = target_road.baseinfo[2]
                                can_pass_road_flag = cur_car.can_pass_road(target_road_speed = target_road_speed)
                            if can_pass_road_flag is True:  # 如果本终止态车辆的速度能通过路口
                                cur_car.change_end_state_car(-1)

                            else:
                                if pre_car_quene[cur_car_laneID] is None:
                                    cur_car.change_end_state_car(1)
                                else:
                                    pre_car = carlist[pre_car_quene[cur_car_laneID][0]]  # 前车对象
                                    pre_car_laneID = pre_car_quene[cur_car_laneID][1]  # 前车所在的车道
                                    pre_car_end_distance = pre_car.end_distance
                                    distance_tofrontcar = cur_car.end_distance - pre_car.end_distance - 1  # 到前车的距离
                                    # 前方有车，但是距离当前车很远，不干扰当前车的正常前进,前方有车但不阻挡，那么不管前车是什么状态，当前车辆都可以保持终止状态
                                    if cur_car.realspeed <= distance_tofrontcar:
                                        cur_car.change_end_state_car(1)
                                    else:
                                        # 有前车阻挡，且前车为等待态
                                        if pre_car.cur_state == -1:  #
                                            cur_car.change_end_state_car(-1)

                                        else:  # 有前车阻挡，且前车为终止态,这就需要先更新real_speed,然后更新end_distance
                                            cur_car.change_end_state_car(1, road_speed=road_baseinfo[2],
                                                                         distance_tofrontcar=distance_tofrontcar)

                                if cur_car.cur_state == 1:
                                    road.change_end_ditance_in_quene(crossID, cur_carID, cur_car_laneID,
                                                                     cur_car.end_distance)
                        ###########################################
                        print('终止态处理函数：{}时刻，{}号道路的{}号车道上的{}号车;'.format(
                        cur_time,roadID,cur_car_laneID,cur_carID))
                        ############################################
                        pre_car_quene[cur_car_laneID] = [cur_carID, cur_car_laneID]
    #路口等待状态车辆处理函数
    def wait_state_car_function(self,cur_time,roadlist,carlist,map_info,schedual_system_info,end_carport_car_num,crosslist):
        has_deadlock = False
        has_car_can_pass_cross = True  #当前路口是否还有车可以通过路口的标记
        cross_baseinfo = self.baseinfo  # 路口基本信息
        crossID = cross_baseinfo[0]
        while (has_car_can_pass_cross):  # 这是保证能通过当前路口的车辆都通过路口
            for roadID in cross_baseinfo[1:]:  # 对当前路口的每一条道路
                if roadID == -1:
                    continue
                else:

                    # 备注：这里不需要在区分是单向道路还是双向道路，因为通过传入当前的crossID,
                    #      可以直接在road对象内选择存储开往当前路口的队列
                    road = roadlist[roadID]
                    if road.baseinfo[-1] == 0 and crossID != road.baseinfo[5]:
                        continue  # 车为单向车道，且当前路口不是道路的出口
                    else:
                        ##现在开始处理当前道路上的等待状态车辆
                        pre_car_quene = [None] * road.baseinfo[3]
                        # 获取道路上一辆车的ID
                        # 获取当前道路按照优先级拍好序的队列
                        sorted_quene = road.sorted_quene(crossID)
                        if sorted_quene == []:
                            continue
                        for first_elem in sorted_quene:
                            cur_carID = first_elem[0]
                            cur_car_end_distance = first_elem[1]
                            cur_car_laneID = first_elem[2]
                            cur_car = carlist[cur_carID] # 获取当前车辆对象
                            if cur_car.cur_state == -1:  # 当前车辆状态为等待态
                                can_pass_road_flag = True
                                target_roadID = cur_car.find_target_roadID() # 获取目标道路ID
                                if target_roadID == -1:
                                    can_pass_road_flag = cur_car.can_pass_road()
                                else:
                                    target_road = roadlist[target_roadID] # 获取目标道路对象
                                    target_road_speed = target_road.baseinfo[2]
                                    can_pass_road_flag = cur_car.can_pass_road(target_road_speed=target_road_speed)

                                if can_pass_road_flag is True:  # 车能通过道路
                                    if pre_car_quene[cur_car_laneID] != None:
                                        pre_carID = pre_car_quene[cur_car_laneID][0]
                                        pre_car_laneID = pre_car_quene[cur_car_laneID][1]
                                        pre_car = carlist[pre_carID]
                                        distance_tofrontcar = cur_car.end_distance - pre_car.end_distance -1
                                        if cur_car.realspeed <= distance_tofrontcar:
                                            cur_car.change_wait_state_car(target_state=1, can_pass_cross=False,
                                                                        road_speed=road.baseinfo[2],
                                                                        distance_tofrontcar=distance_tofrontcar)
                                        else:
                                            if pre_car.cur_state == -1:
                                                cur_car.cur_state = -1
                                            else:
                                                cur_car.change_wait_state_car(target_state=1, can_pass_cross=False,
                                                                              road_speed=road.baseinfo[2],
                                                                              distance_tofrontcar=distance_tofrontcar)
                                        pre_car_quene[cur_car_laneID] = [cur_carID, cur_car_laneID]
                                    else:
                                        if cur_car.is_final_cross(crossID) is True:  # 当前路口是当前车的最终目的地
                                            cur_car.change_wait_state_car(target_state=0,cur_time = cur_time)
                                            self.enquene_end_carport(cur_carID)
                                            End_carport_car_num.end_carport_car_num += 1
                                            road.dequene_car(crossID, cur_car_laneID)  # 将当前车弹出当前道路
                                            ###########################################
                                            # 输出某车，在t时刻从道路的几车道进入几号路口的终点车库
                                            print('入库数：{} | {}号车，在{}时刻，从道路{}的{}车道进入{}号路口终点车库;调用等待态函数：{} '.format(
                                                End_carport_car_num.end_carport_car_num,
                                                cur_car.baseinfo[0],cur_time,cur_car.cur_road,cur_car_laneID,crossID,Call_wait_state_car_time.call_wait_state_car_num))
                                            #######################
                                        else:
                                            ## 检查目标道路是否允许车辆进入
                                            # 获取目标道路最后一个元素
                                            last_elem = target_road.last_car(crossID)  # 可为：1 or [start_distance,laneID]

                                            if last_elem == -1:  # 当前目标道路已满

                                                #设置为终止态，等待下一时刻处理
                                                cur_car.cur_state = 1
                                                pre_car_quene[cur_car_laneID] =[cur_carID, cur_car_laneID]

                                            else:  # 目标道路有空余的车位，允许进入目标道路
                                                exist_conflict = False  # 用来统一冲突问题
                                                distance_tofrontcar = last_elem[0] + cur_car.end_distance
                                                target_laneID = last_elem[1]
                                                # 检查路口行驶方向是否有冲突
                                                exist_conflict = self.check_if_conflict(roadlist, carlist, cur_car)
                                                ##对冲突与否做处理
                                                if exist_conflict is False:  # 不存在冲突
                                                    target_road_speed = target_road.baseinfo[2]
                                                    target_road_length = target_road.baseinfo[1]
                                                    cur_car.change_wait_state_car(target_state=1,
                                                                                  distance_tofrontcar=distance_tofrontcar,
                                                                                  can_pass_cross=True,
                                                                                  target_roadID=target_roadID,
                                                                                  target_road_speed=target_road_speed,
                                                                                  target_road_length=target_road_length)
                                                    #设置下一次转向
                                                    if cur_car.baseinfo[2] == crossID:
                                                        pass
                                                    else:
                                                        cur_car.set_car_direction( roadlist, crosslist, crossID)
                                                    # 当前车通过路口，加入目标车道
                                                    target_road.enquene_car(cur_carID, cur_car.end_distance,
                                                                           crossID, target_laneID)
                                                    road.dequene_car(crossID, cur_car_laneID)  # 将当前车弹出当前车道
                                                    ###################################################################

                                                    print('{}时刻{}号车在从{}号道路的{}号车道，通过{}号路口，进入{}号道路的{}车道;调用等待态函数：{}次'.format(
                                                        cur_time,cur_carID,roadID,cur_car_laneID,crossID,target_roadID,target_laneID,Call_wait_state_car_time.call_wait_state_car_num
                                                    ))
                                                    #########################################################
                                                else:  # c冲突了，换到下一条车道
                                                    continue #这里直接处理为跳到下一条道

                                else:  # 当前等待态车辆不能通过路口
                                    if pre_car_quene[cur_car_laneID] == None:  # 没有前车阻挡
                                        distance_tofrontcar = cur_car.end_distance
                                        cur_car.change_wait_state_car(target_state=1,can_pass_cross=False,road_speed = road.baseinfo[2],distance_tofrontcar= distance_tofrontcar)

                                    else:  # 有前车
                                        pre_carID = pre_car_quene[cur_car_laneID][0]
                                        pre_car_laneID = pre_car_quene[cur_car_laneID][1]
                                        pre_car = carlist[pre_carID]  # 前车

                                        pre_car_end_distance = pre_car.end_distance
                                        distance_tofrontcar = cur_car.end_distance - pre_car.end_distance - 1
                                        cur_car.change_wait_state_car(target_state=1, can_pass_cross=False,
                                                                      road_speed=road.baseinfo[2],
                                                                      distance_tofrontcar=distance_tofrontcar)
                                    pre_car_quene[cur_car_laneID] = [cur_carID, cur_car_laneID]

                                    road.change_end_ditance_in_quene(crossID, cur_carID, cur_car_laneID,
                                                                     cur_car.end_distance)
                                ##################################################
                                print('{}时刻处理{}号路口等待态的{}号车'.format(cur_time,crossID,cur_carID))
                                ################################################
                            else:  # 遇到终止态的车了，跳出当前循环
                                continue
                print('{}时刻，等待态函数处理完{}号路口'.format(cur_time, crossID))
            #########################################################
            # 检查当前路口是否还有车可以通过路口
            call_wait_state_car_num=Call_wait_state_car_time.call_wait_state_car_num
            has_car_can_pass_cross = self.check_has_car_can_pass(roadlist,carlist)