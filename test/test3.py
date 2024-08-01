import re


def generate_custom_list(keyword, n):
    # 生成前 n 个元素
    custom_list = [f'{keyword}_{i}_main_Curve_con' for i in range(1, n + 1)]

    # 添加最后一个元素
    custom_list.append('rigF_JointEnd_Curve_con')

    return custom_list


# 示例调用
keyword = 'tentacleF'
n = 33
a = generate_custom_list(keyword, n)
print(a)
b = generate_custom_list(keyword, n)
c = generate_custom_list(keyword, n)

x = "rigF_Cons_curve"
y = "rig_Cons_Y_curve"
z = "rig_Cons_Z_curve"


def aaaa(a, b):
    curve = FBFindModelByLabelName(a)
    obj_list = []
    for i in b:
        obj_list.append(FBFindModelByLabelName(i))
    for index, obj in enumerate(obj_list):
        curve.PathKeySetControlNode(index, obj)


aaaa(x, a)
aaaa(y, b)
aaaa(z, c)