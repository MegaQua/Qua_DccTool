import re

a = ['tentacle1_main_con', 'tentacle2_main_con', 'tentacle3_main_con', 'tentacle4_main_con', 'tentacle5_main_con', 'tentacle6_main_con',
     'tentacle7_main_con', 'tentacle8_main_con', 'tentacle9_main_con', 'tentacle10_main_con', 'rig_JointEnd_con']
b = ['tentacle1_main_con_Y', 'tentacle2_main_con_Y', 'tentacle3_main_con_Y', 'tentacle4_main_con_Y', 'tentacle5_main_con_Y', 'tentacle6_main_con_Y',
     'tentacle7_main_con_Y', 'tentacle8_main_con_Y', 'tentacle9_main_con_Y', 'tentacle10_main_con_Y', 'rig_JointEnd_con_Y']
c = ['tentacle1_main_con_Z', 'tentacle2_main_con_Z', 'tentacle3_main_con_Z', 'tentacle4_main_con_Z', 'tentacle5_main_con_Z', 'tentacle6_main_con_Z',
     'tentacle7_main_con_Z', 'tentacle8_main_con_Z', 'tentacle9_main_con_Z', 'tentacle10_main_con_Z', 'rig_JointEnd_con_Z']

pattern = re.compile(r'tentacle(\d+)_main_con')

a = [pattern.sub(r'rig_con \1', item) for item in a]
b = [pattern.sub(r'rig_con \1', item) for item in b]
c = [pattern.sub(r'rig_con \1', item) for item in c]

x = "rig_Cons_curve"
y ="rig_Cons_Y_curve"
z ="rig_Cons_Z_curve"
print(a)
print(b)
print(c)



def aaaa(a, b):
    curve=FBFindModelByLabelName(a)
    obj_list=[]
    for i in b:
        obj_list.append(FBFindModelByLabelName(i))
    for index, obj in enumerate(obj_list):
        curve.PathKeySetControlNode(index, obj)

aaaa(x,a)
aaaa(y,b)
aaaa(z,c)