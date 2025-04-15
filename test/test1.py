from pyfbsdk import *
a = ['tentacle1_main_con', 'tentacle2_main_con', 'tentacle3_main_con', 'tentacle4_main_con', 'tentacle5_main_con', 'tentacle6_main_con',
     'tentacle7_main_con', 'tentacle8_main_con', 'tentacle9_main_con', 'tentacle10_main_con', 'rig_JointEnd_con']

x = "rig_Cons_curve"

def connectObjToCurve(a, b):
    curve=FBFindModelByLabelName(a)
    obj_list=[]
    for i in b:
        obj_list.append(FBFindModelByLabelName(i))
    for index, obj in enumerate(obj_list):
        curve.PathKeySetControlNode(index, obj)

connectObjToCurve(x,a)
