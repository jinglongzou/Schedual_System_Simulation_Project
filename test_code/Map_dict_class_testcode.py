# 创建地图需要先读取道路、路口信息
# 以路口为节点，根据路口数，来构建邻接表

root = 'E:\\CodeProgram\\PythonProgram\\myPyCharmProject\\huaweicodecontest\\new_huaweiprogram\\new_simulation_files\\1-map-training-1\\' # txt文件和当前脚本在同一目录下，所以不用写具体路径
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

from Map_Class_dict import Map
car_map = Map(road_dict,cross_dict)
print(car_map.get_edge(1,2))
adjMatrix = car_map.build_adjMatrix()

path_length,path = car_map.all_shortest_paths_floyd()
import pandas as pd
'''
df1 = pd.DataFrame(path)
df1.to_excel('path.xls')
df2 = pd.DataFrame(path_length)
df2.to_excel('path_length.xls')
df3 = pd.DataFrame(adjMatrix)
df3.to_excel('adjMatrix.xls')
'''
start_cross = 37
end_cross = 1
cross_path,road_path = car_map.find_shortest_path(start_cross,end_cross)
print(road_path)
'''
print(car_map.get_head()[1].elem)
print('\n')
print(car_map.build_adjMatrix()[:5])
print('\n')
print(path_length[:5])
'''