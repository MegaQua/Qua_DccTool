import maya.cmds as cmds
import os

folder_path = r"S:\Public\qiu_yi\JCQ_Tool\codes\mel"

config_path = cmds.internalVar(userAppDir=True)
maya_version = cmds.about(version=True)
scripts_folder = os.path.join(config_path, maya_version, "scripts")
shelf_name = "AriMel"
element_to_keep = ""


# 查询指定名称的shelfLayout是否存在
shelf_exists = cmds.shelfLayout(shelf_name, query=True, exists=True)

if shelf_exists:
    shelf_items = cmds.shelfLayout(shelf_name, query=True, childArray=True)

    if shelf_items:
        # 遍历shelfLayout中的子元素
        for item in shelf_items:
            item_name = cmds.shelfButton(item, query=True, label=True)

            # 检查元素名称是否匹配要保留的名称
            if item_name != element_to_keep:
                # 删除不匹配的元素
                cmds.deleteUI(item)
else:
    cmds.shelfLayout(shelf_name, p="ShelfLayout")

for file_name in folder_path:
    if not file_name.endswith(".mel"):
        continue  # 跳过非Python脚本文件
    if file_name == element_to_keep+".mel":
        continue  # 跳过指定文件名
    # 获取Python脚本文件的完整路径
    script_path = os.path.join(scripts_folder, file_name)

    # 获取对应的图标文件的完整路径
    toolname = file_name[:-3]
    icon_path = os.path.join(icon_folfer, file_name[:-3] + ".png")

    if not os.path.isfile(icon_path):
        icon_path = scripts_folder+ "noimage.png"

    cmds.shelfButton(label=toolname, command=toolname, sourceType="mel", image=icon_path)


