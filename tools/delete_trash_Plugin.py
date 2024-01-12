import maya.cmds as cmds

# 删除未知节点
cmds.delete(cmds.ls(type="unknown"))

# 删除未知插件
plugins_list = cmds.unknownPlugin(q=True, l=True)
if plugins_list:
    for plugin in plugins_list:
        print(plugin)
        if cmds.unknownPlugin(plugin, q=True, l=True):  # 检查插件是否被锁定
            cmds.unknownPlugin(plugin, e=True, unlock=True)  # 解锁插件
        cmds.unknownPlugin(plugin, r=True)
