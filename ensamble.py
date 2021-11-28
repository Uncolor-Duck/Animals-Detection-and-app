import os
import json
import os.path as osp
import cv2
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPoint

"""
阈值设定
"""
thr = 0.5

"""
函数定义区
"""
def IoU_cal(line1, line2):
    a = np.array(line1).reshape(4, 2)  # 四边形二维坐标表示
    poly1 = Polygon(a).convex_hull  # python四边形对象，会自动计算四个点，最后四个点顺序为：左上 左下  右下 右上 左上
    b = np.array(line2).reshape(4, 2)
    poly2 = Polygon(b).convex_hull

    union_poly = np.concatenate((a, b))  # 合并两个box坐标，变为8*2
    # print(union_poly)
    if not poly1.intersects(poly2):  # 如果两四边形不相交
        iou = 0
    else:
        try:
            inter_area = poly1.intersection(poly2).area  # 相交面积
            # union_area = poly1.area + poly2.area - inter_area
            S1 = MultiPoint(a).convex_hull.area
            S2 = MultiPoint(b).convex_hull.area
            union_area = S1 + S2 - inter_area
            if union_area == 0:
                iou = 0
                return iou
            iou = float(inter_area) / union_area
        except shapely.geos.TopologicalError:
            print('shapely.geos.TopologicalError occured, iou set to 0')
            iou = 0
    return iou

def write_txt(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        data = line.split(' ')
        img_id, pro, x1, y1, x2, y2, x3, y3, x4, y4 = data[0], data[1], data[2], data[3], data[4], data[5], data[6], \
                                                      data[7], data[8], data[9]
        class_name = input_path.split('/')[-1].split('.')[0].split('_')[-1]
        output_dir = [class_name, ' ', pro, ' ', x1, ' ', y1, ' ', x2, ' ', y2, ' ', x3, ' ', y3, ' ', x4, ' ', y4]
        txt_path = osp.join(output_path, img_id + '.txt')
        with open(txt_path, 'a+') as f:
            f.writelines(output_dir)

def change(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()
    objects = []
    for i, line in enumerate(lines):
        data = line.split(' ')
        class_name, pro, x1, y1, x2, y2, x3, y3, x4, y4 = data[0], data[1], data[2], data[3], data[4], data[5], data[6], \
                                                          data[7], data[8], data[9]
        objects.append([i, class_name, pro, x1, y1, x2, y2, x3, y3, x4, y4])
    for i, object in enumerate(objects):
        num_one = object[0]
        pro_one = object[2]
        line1 = list(map(float, object[3:]))
        for j, obj in enumerate(objects):
            yeah = 'T'
            num_two = obj[0]
            pro_two = obj[2]
            line2 = list(map(float, obj[3:]))
            if num_two == num_one:
                continue
            else:
                iou = IoU_cal(line1, line2)
            if float(iou) >= thr and pro_one < pro_two and object[1] == obj[1]:
                print(iou)
                yeah = 'Y'
                break
            if float(iou) == 1.0 and pro_one == pro_two and object[1] == obj[1] and i <= j:
                print(iou)
                yeah = 'Y'
                break
        if yeah == 'Y':
            continue
        with open(output_path, 'a+') as f:
            object = list(map(str, object))
            data_output = object[1] + ' ' + object[2] + ' ' + object[3] + ' ' + object[4] + ' ' +\
                          object[5] + ' ' + object[6] + ' ' + object[7] + ' ' + object[8] + ' ' +\
                          object[9] + ' ' + object[10]
            f.writelines(data_output)

def writedown(input_path, output_dir, img_id):
    with open(input_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        data = line.split(' ')
        class_name, pro, x1, y1, x2, y2, x3, y3, x4, y4 = data[0], data[1], data[2], data[3], data[4], data[5],\
                                                          data[6], data[7], data[8], data[9]
        output_path = osp.join(output_dir, 'Task1_'+class_name+'.txt')
        with open(output_path, 'a+') as f:
            output = img_id + ' ' + pro + ' ' + x1 + ' ' + y1 + ' ' + x2 + ' ' + y2 + ' ' + x3 + ' ' + y3 + ' ' +\
                     x4 + ' ' + y4
            f.writelines(output)

def inter_load(input_one_path, input_two_path, output_path, img_id):
    lines_one, lines_two = '', ''
    output_img_path = osp.join(output_path, img_id)
    if input_one_path != 'None':
        with open(input_one_path, 'r') as f:
            lines_one = f.readlines()
    if input_two_path != 'None':
        with open(input_two_path, 'r') as f:
            lines_two = f.readlines()
    for line_one in lines_one:
        for line_two in lines_two:
            one_data, two_data = line_one.split(' '), line_two.split(' ')
            class_one, pro_one, x1_one, y1_one, x2_one,\
            y2_one, x3_one, y3_one, x4_one, y4_one = one_data[0], one_data[1], one_data[2], one_data[3], one_data[4],\
                                                     one_data[5], one_data[6], one_data[7], one_data[8], one_data[9]
            class_two, pro_two, x1_two, y1_two, x2_two,\
            y2_two, x3_two, y3_two, x4_two, y4_two = two_data[0], two_data[1], two_data[2], two_data[3], two_data[4],\
                                                     two_data[5], two_data[6], two_data[7], two_data[8], two_data[9]
            line1 = list(map(float, one_data[2:]))
            line2 = list(map(float, two_data[2:]))
            iou = IoU_cal(line1, line2)
            if iou >= thr and class_one == class_two:
                print(iou)
                with open(output_img_path, 'a+') as f:
                    if pro_one >= pro_two:
                        output_data = class_one + ' ' + pro_one + ' ' + x1_one + ' ' + y1_one + ' ' + x2_one\
                                      + ' ' + y2_one + ' ' + x3_one + ' ' + y3_one + ' ' + x4_one + ' ' + y4_one
                    else:
                        output_data = class_two + ' ' + pro_two + ' ' + x1_two + ' ' + y1_two + ' ' + x2_two \
                                        + ' ' + y2_two + ' ' + x3_two + ' ' + y3_two + ' ' + x4_two + ' ' + y4_two
                    f.writelines(output_data)
                    break


if __name__ == '__main__':
    """
    初始化部分
    """
    model_one, model_two = 'D:\data\model_ensamble\\boats\\v2+v3\Task1_results_nms\\', 'D:\data\model_ensamble\\boats\\redet\Task1_results_nms\\'  # 两个模型的output保留位置
    txt_down = 'D:\data\json\down\\'  # 两个模型的txt保留位置,最好与output处于一个文件夹
    txt_load = 'D:\data\json\load\\'  # 两个模型的txt保留位置,最好与output处于一个文件夹。其与down不同
    output_path = 'D:\data\json\\'  # 返回的output,注意，一定要为空或者不存在！！！
    txt_inter_path = osp.join(output_path, 'inter')
    change_mode = 'union'        #模式，union表示并集模式，inter表示交集
    mode_list = ['union', 'union', 'union', 'inter', 'inter', 'inter', 'inter', 'inter', 'union', 'union']
    """
    创建文件夹部分
    """
    if not osp.exists(output_path):
        os.mkdir(output_path)
    if not osp.exists(txt_load):
        os.mkdir(txt_load)
    if not osp.exists(txt_down):
        os.mkdir(txt_down)
    if not osp.exists(txt_inter_path):
        os.mkdir(txt_inter_path)
    """
    第一步，将两个model的output直接取交集
    """
    input_one_lists = os.listdir(model_one)
    input_two_lists = os.listdir(model_two)
    #if change_mode == 'union':
    for i, input_one_list in enumerate(input_one_lists):
        if mode_list[i] == 'union':
        #if input_one_list == 'Task1_02.txt':
            input_path = osp.join(model_one, input_one_list)
            output = txt_down
            write_txt(input_path, output)
            #break
    for i, input_two_list in enumerate(input_two_lists):
        if mode_list[i] == 'union':
#       if input_two_list == 'Task1_01.txt':
            input_path = osp.join(model_two, input_two_list)
            output = txt_down
            write_txt(input_path, output)
#          break
        """
        第二步，逐个取IoU，计算是否为重叠部分
        """
    down_lists = os.listdir(txt_down)
    for down_list in down_lists:
        input_path = osp.join(txt_down, down_list)
        output = osp.join(txt_load, down_list)
        change(input_path, output)

        """
        第三步，还原为原本形式
        """
    load_lists = os.listdir(txt_load)
    for load_list in load_lists:
        input_path = osp.join(txt_load, load_list)
        output_path = output_path
        img_id = load_list.split('.')[0]
        writedown(input_path, output_path, img_id)
    #elif change_mode == 'inter':
        """
        第一步，分别将两个模型的结果转为图片
        """
    txt_down_model_1 = osp.join(txt_inter_path, 'model1')
    txt_down_model_2 = osp.join(txt_inter_path, 'model2')
    if not osp.exists(txt_down_model_1):
        os.mkdir(txt_down_model_1)
    if not osp.exists(txt_down_model_2):
        os.mkdir(txt_down_model_2)
    for i, input_one_list in enumerate(input_one_lists):
        if mode_list[i] == 'inter':
            # if input_one_list == 'Task1_02.txt':
            input_path = osp.join(model_one, input_one_list)
            output = txt_down_model_1
            write_txt(input_path, output)
            # break
    for i, input_two_list in enumerate(input_two_lists):
        if mode_list[i] == 'inter':
            #       if input_two_list == 'Task1_01.txt':
            input_path = osp.join(model_two, input_two_list)
            output = txt_down_model_2
            write_txt(input_path, output)
    #          break
    txt_down_inter = osp.join(txt_inter_path, 'down')
    if not osp.exists(txt_down_inter):
        os.mkdir(txt_down_inter)
    inter_model1_lists = os.listdir(txt_down_model_1)
    inter_model1_lists_copy = os.listdir(txt_down_model_1)
    inter_model2_lists = os.listdir(txt_down_model_2)
    """
        第一步，分别将两个模型的结果转为图片
    """
    for inter_model2_list in inter_model2_lists:
        if inter_model2_list not in inter_model1_lists:
            inter_model1_lists_copy.append(inter_model2_list)
    for inter_model1_list in inter_model1_lists_copy:
        input_one = osp.join(txt_down_model_1, inter_model1_list)
        input_two = osp.join(txt_down_model_2, inter_model1_list)
        if inter_model1_list in inter_model1_lists and inter_model1_list in inter_model2_lists:
            inter_load(input_one, input_two, txt_down_inter, inter_model1_list)
        elif inter_model1_list in inter_model2_lists and inter_model1_list not in inter_model2_lists:
            inter_load(input_one, 'None', txt_down_inter, inter_model1_list)
        elif inter_model1_list not in inter_model2_lists and inter_model1_list in inter_model2_lists:
            inter_load('None', input_two, txt_down_inter, inter_model1_list)
        else:
            print('wrong')
    load_lists_inter = os.listdir(txt_down_inter)
    for load_list in load_lists_inter:
        input_path = osp.join(txt_down_inter, load_list)
        output_path = output_path
        img_id = load_list.split('.')[0]
        writedown(input_path, output_path, img_id)