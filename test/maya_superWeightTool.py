import maya.cmds as cmds
import maya.mel as mel


def copy_skin_weights_between_objects(source_obj, target_obj):
    # 获取源对象的蒙皮节点
    skin_cluster = cmds.ls(cmds.listHistory(source_obj), type='skinCluster')
    if not skin_cluster:
        cmds.warning(f"No skinCluster found on the object {source_obj}.")
        return
    skin_cluster = skin_cluster[0]

    # 获取目标对象的蒙皮骨骼
    jnt_list = cmds.skinCluster(skin_cluster, query=True, inf=True)

    # 查询目标对象是否有蒙皮信息，如果有就删除
    target_skin_cluster = cmds.ls(cmds.listHistory(target_obj), type='skinCluster')
    if target_skin_cluster:
        cmds.delete(target_skin_cluster)

    # 给目标对象进行蒙皮，并获取新蒙皮节点的名称
    new_skin_cluster = cmds.skinCluster(jnt_list, target_obj, tsb=True)[0]

    # 拷贝蒙皮权重
    cmds.copySkinWeights(ss=skin_cluster, ds=new_skin_cluster, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='oneToOne')


def main():
    # 获取当前选择的对象
    list_select = cmds.ls(sl=True)

    if not list_select:
        cmds.warning("Please select at least one object.")
        return

    # 如果只选择了一个对象，则仅复制并拷贝权重
    if len(list_select) == 1:
        original_obj = list_select[0]
        backup_name = f"{original_obj}_weightcopy"
        backup = cmds.duplicate(original_obj, name=backup_name)[0]
        copy_skin_weights_between_objects(original_obj, backup)
    else:
        # 创建备份对象并记录备份对象的名称
        backups = []
        for obj in list_select:
            backup = cmds.duplicate(obj, name=f"{obj}_backup")[0]
            backups.append(backup)

            # 拷贝蒙皮权重
            copy_skin_weights_between_objects(obj, backup)

        # 使用mel命令polyUniteSkinned合并备份对象并保留蒙皮信息
        combined = mel.eval(f'polyUniteSkinned -ch 1 -mergeUVSets 1 -centerPivot {" ".join(backups)}')[0]

        # 构建合并后的对象名称
        combined_name = "".join([obj[0].upper() for obj in list_select]) + "_weightcopy"

        # 复制合并后的对象并重命名
        final_obj = cmds.duplicate(combined, name=combined_name)[0]

        # 拷贝合并后的权重到最终对象
        copy_skin_weights_between_objects(combined, final_obj)

        # 删除合并对象历史
        cmds.delete(combined, ch=True)

        # 删除合并对象
        cmds.delete(combined)

        # 删除备份对象
        cmds.delete(backups)


# 调用函数执行拷贝蒙皮权重的操作
main()
