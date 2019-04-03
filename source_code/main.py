'''
这里是实现调度系统主逻辑
#第一步初始化创建路口、道路、车辆
for 时间片：
    for 路口：
        for 道路：
            for 车辆
'''
###############################################################
#1、读取数据
#创建出road_dict,car_dict,cross_dict
##############################################################
root = 'E:\\CodeProgram\\PythonProgram\\myPyCharmProject\\huaweicodecontest\\huaweiprogram\\1-map-training-1\\' # txt文件和当前脚本在同一目录下，所以不用写具体路径

def read_txt(data_dict,filename):
    with open(filename, 'r') as file_to_read:
        lines = file_to_read.readlines()
        for line in lines[1:]:
            line = line.replace(')','')
            line = line.replace('(','')
            line = [int(i) for i in line.strip('\n').split(', ')]
            if line[0] not in data_dict.keys():
                data_dict[line[0]] = line
            #data_dict[line[0]] = line
    return data_dict
#读取道路数据
road_filename = root + 'road.txt'
road_dict = {}
road_dict = read_txt(road_dict,road_filename)
#读取路口数据
cross_filename = root + 'cross.txt'
cross_dict = {}
cross_dict = read_txt(cross_dict,cross_filename)
#读取车辆数据
car_filename = root + 'car.txt'
car_dict = {}
car_dict = read_txt(car_dict,car_filename)
#################################################
#2、创建地图对象
#################################################
from Map_Class_dict import Map
map_info = Map(road_dict,cross_dict)
################################################
#3、创建车辆、道路、路口的对象几何
################################################
#创建道路对象集合
roadlist= {}
from Road_Class_list import road_class
for value in road_dict.values():
    #if key not in roadlist.keys():
    roadlist[value[0]] = road_class(value)
#创建路口对象集合
crosslist ={}
from Cross_Class import cross_class
for value in cross_dict.values():
    # if key not in crosslist.keys():
    crosslist[value[0]] = cross_class(value)
#创建车辆对象集合
carlist = {}
from Car_Class import car_class
for value in car_dict.values():
    carlist[value[0]] = car_class(value)
#####################################################
#4、将车辆加入未出发库
######################################################
car_num = 0 #车辆总数
for car in carlist.values():
    crossID = car.baseinfo[1] #起点路口ID
    elem = [car.baseinfo[-1],car.baseinfo[0]] # plantime, carID
    crosslist[crossID].enquene_begin_carport(elem)
    car_num  += 1
#############################################################
#5、开始调度，从1时刻开始；
from GlobalVar import Call_end_state_car_time,Call_wait_state_car_time,Call_start_car_time,Cur_Time,End_carport_car_num
start_car_num = 0
end_carport_car_num = End_carport_car_num.end_carport_car_num #初始化入库车辆

cur_time = Cur_Time.cur_time #初始化当前时间
schedual_system_info = None #初始化调度系统信息
while(end_carport_car_num < car_num):
    ## 首先处理各个路口各个道路上的终止状态车辆，这个过程只经历一次## 由于一个时间片内，终止状态车辆只能处理一次
    for cross in crosslist.values(): #对每一个路口
        cross.end_state_car_function(cur_time,roadlist,carlist)
    ## 然后处理当前路口各个道路上的等待状态车辆，这个过程可经历多次##
    has_deadlock = True
    while (has_deadlock):  # 这是保证在一个时间片结束后没有死锁
        # 这个参数有点问题：不能用是否还有等待态在路口，因为没有死锁，车辆可以在路口等待一个或几个时刻
        for cross in crosslist.values():  # 对每一个路口
            cross.wait_state_car_function(cur_time,roadlist,carlist,map_info,schedual_system_info,end_carport_car_num,crosslist)
        # 检查是否有死锁
        has_deadlock = False
    ## 将可以出发的车辆出发：
    for cross in crosslist.values():  # 对每一个路口
        cross.start_car_on_cross(cur_time, roadlist, carlist, map_info, schedual_system_info,crosslist)
    #函数调用次数统计
    call_start_car_time = Call_start_car_time.call_start_car_time
    call_end_state_car_num = Call_end_state_car_time.call_end_state_car_num
    call_wait_state_car_num = Call_wait_state_car_time.call_wait_state_car_num
    #时间更新
    Cur_Time.cur_time +=1
    cur_time = Cur_Time.cur_time
    print('车辆总数：{}；入库车辆数：{}。'.format(car_num,End_carport_car_num.end_carport_car_num))







