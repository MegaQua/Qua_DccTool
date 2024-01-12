import maya.cmds as cmds


def create_joint_at_avg_center():
    # 获取当前选中的顶点
    selected_vertices = cmds.ls(selection=True, flatten=True)

    # 如果没有选择任何点，则退出
    if not selected_vertices:
        cmds.warning("Please select some vertices.")
        return

    # 初始化坐标的总和
    total_x, total_y, total_z = 0.0, 0.0, 0.0

    # 对于每个顶点，获得它的世界空间坐标，并累加
    for vert in selected_vertices:
        pos = cmds.pointPosition(vert, world=True)
        total_x += pos[0]
        total_y += pos[1]
        total_z += pos[2]

    # 计算坐标的平均值
    avg_x = total_x / len(selected_vertices)
    avg_y = total_y / len(selected_vertices)
    avg_z = total_z / len(selected_vertices)

    # 在平均坐标处创建一个joint
    cmds.select(deselect=True)
    cmds.joint(p=(avg_x, avg_y, avg_z))


# 执行函数
create_joint_at_avg_center()
