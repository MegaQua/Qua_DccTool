import os
import maya.cmds as cmds
folder_path = r"S:\Public\qiu_yi\JCQ_Tool\codes"
py_folder = folder_path+r"\tools"
icon_folfer =folder_path+r"\toolsicon"
doc_folfer =folder_path+r"\toolsdoc"
#py_names = [f for f in os.listdir(py_folfer) if os.path.isfile(os.path.join(py_folfer, f))]

# 创建一个新的Shelf
shelf_name = "JCQtool"
try:
    cmds.deleteUI(shelf_name)
except:
    pass

cmds.shelfLayout(shelf_name, p="ShelfLayout")

file_list = os.listdir(py_folder)
file_list.sort(key=lambda x: x.lower())

for file_name in file_list:
    if not file_name.endswith(".py"):
        continue  # 跳过非Python脚本文件

    # 获取Python脚本文件的完整路径
    script_path = os.path.join(py_folder, file_name)

    # 获取对应的图标文件的完整路径
    icon_path = os.path.join(icon_folfer, file_name[:-3] + ".png")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(icon_folfer, "noimage.png")
    doc_path = os.path.join(doc_folfer, file_name[:-3] + ".png")
    if not os.path.exists(doc_path):
        doc_path = os.path.join(doc_path, "noimage.png")
    command = '''\
path = r"{0}"
exec(compile(open(path, 'rb').read(), path, 'exec'))'''.format(script_path)

    image_path = r'S:\Public\qiu_yi\JCQ_Tool\codes\toolsdoc\noimage.png'
    dc = '''\
import subprocess
subprocess.Popen(['start', r"{0}"], shell=True)'''.format(doc_path)

    button=cmds.shelfButton(
        command=command,
        image=icon_path,
        label=file_name[:-3],  # 移除文件扩展名作为按钮的标签
        parent=shelf_name,
        dcc=dc
    )
    # 为这个按钮创建一个右键菜单

def onMayaDroppedPythonFile():
    # 在这里放置你的代码
    pass
    # ... 其他代码 ...
