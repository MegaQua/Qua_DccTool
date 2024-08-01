from pyfbsdk import *

def connectObjToCurve(a,b):
    # 获取当前场景中的所有物体
    scene = FBSystem().Scene
    selected_objects = [obj for obj in scene.Components if obj.Selected]
    print(selected_objects)

    curve =FBFindModelByLabelName(a)
    # 第一个选中的物体作为曲线，其余的物体作为连接的对象
    #curve = selected_objects[0]
    obj_list=[]
    for i in b
        obj_list.append(FBFindModelByLabelName(i))



    # 执行连接操作
    for index, obj in enumerate(obj_list):
        curve.PathKeySetControlNode(index, obj)

# Example usage
connectObjToCurve("rig_Cons_curve",['tentacle1_copy_con', 'tentacle2_copy_con', 'tentacle3_copy_con', 'tentacle4_copy_con', 'tentacle5_copy_con', 'tentacle6_copy_con', 'tentacle7_copy_con', 'tentacle8_copy_con', 'tentacle9_copy_con', 'tentacle10_copy_con', 'rig_JointEnd_con'])
connectObjToCurve("rig_Cons_Y_curve",['tentacle1_copy_con_Y', 'tentacle2_copy_con_Y', 'tentacle3_copy_con_Y', 'tentacle4_copy_con_Y', 'tentacle5_copy_con_Y', 'tentacle6_copy_con_Y', 'tentacle7_copy_con_Y', 'tentacle8_copy_con_Y', 'tentacle9_copy_con_Y', 'tentacle10_copy_con_Y', 'rig_JointEnd_con_Y'])
connectObjToCurve("rig_Cons_Z_curve",['tentacle1_copy_con_Z', 'tentacle2_copy_con_Z', 'tentacle3_copy_con_Z', 'tentacle4_copy_con_Z', 'tentacle5_copy_con_Z', 'tentacle6_copy_con_Z', 'tentacle7_copy_con_Z', 'tentacle8_copy_con_Z', 'tentacle9_copy_con_Z', 'tentacle10_copy_con_Z', 'rig_JointEnd_con_Z'])
