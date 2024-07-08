import maya.cmds as cmds

def check_and_fix_weights(skin_cluster_name, max_influences=4):
    def round_and_cut(weight, decimals=2):
        rounded_weight = round(weight, decimals)
        str_weight = f"{rounded_weight:.{decimals}f}"
        cut_weight = float(str_weight)
        return cut_weight

    # 检查指定的skinCluster
    if not cmds.objExists(skin_cluster_name):
        print("SkinCluster", skin_cluster_name, "does not exist.")
        return

    print("Checking and fixing skinCluster:", skin_cluster_name)

    all_ok = True  # 标志用于跟踪是否所有顶点都没有问题

    # 获取绑定的几何体
    geometry = cmds.skinCluster(skin_cluster_name, q=True, geometry=True)[0]
    vertices = cmds.ls(geometry + ".vtx[*]", flatten=True)

    for vertex in vertices:
        # 获取顶点的权重值和对应的关节
        weights = cmds.skinPercent(skin_cluster_name, vertex, q=True, value=True)
        joint_influences = cmds.skinPercent(skin_cluster_name, vertex, q=True, transform=None)

        # 筛选出权重不为零的数值
        non_zero_weights = [(joint, weight) for joint, weight in zip(joint_influences, weights) if weight > 0]

        if len(non_zero_weights) > max_influences:
            all_ok = False
            print(f"Vertex {vertex} has more than {max_influences} influences: {non_zero_weights}")
            # 按权重值排序
            non_zero_weights.sort(key=lambda x: x[1])
            # 从小到大将权重归零直到剩下max_influences个位置
            for i in range(len(non_zero_weights) - max_influences):
                joint_to_remove, weight_to_remove = non_zero_weights[i]
                print(f"Removing influence: {joint_to_remove} with weight: {weight_to_remove}")
                cmds.skinPercent(skin_cluster_name, vertex, transformValue=[(joint_to_remove, 0)])
            non_zero_weights = non_zero_weights[-max_influences:]

        # 对非零权重值处理前max_influences-1个
        for i in range(len(non_zero_weights) - 1):
            joint, weight = non_zero_weights[i]
            rounded_weight = round_and_cut(weight, 2)  # 四舍五入并截断到小数点后两位
            non_zero_weights[i] = (joint, rounded_weight)
            if weight != rounded_weight:
                all_ok = False
                print(f"Rounding weight for joint {joint} on vertex {vertex} from {weight} to {rounded_weight}")

        # 设定新的权重值
        for joint, final_weight in non_zero_weights:
            cmds.skinPercent(skin_cluster_name, vertex, transformValue=[(joint, final_weight)])

        # 打印点的名字和处理后的非零数值
        print(
            f"Vertex {vertex} now has {len(non_zero_weights)} non-zero weights: {non_zero_weights}")

    if all_ok:
        print("All vertices in the selected object have no issues.")

# 仅操作名为 'skinCluster8' 的皮肤绑定对象，默认最大影响为4
check_and_fix_weights('skinCluster9')
