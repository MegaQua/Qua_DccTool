import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore


class MR_Window(QtWidgets.QWidget):

    # 构造函数
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARkit bs52 adv5 builder")

        layout = QtWidgets.QGridLayout(self)

        arkit_bs_name_label = QtWidgets.QLabel("ar bs name:")
        self.arkit_bs_name_text = QtWidgets.QLineEdit("blendShape1")
        layout.addWidget(arkit_bs_name_label, 0, 0)
        layout.addWidget(self.arkit_bs_name_text, 0, 1)

        get_from_select_btn = QtWidgets.QPushButton("import arbase")
        get_from_select_btn.clicked.connect(self.import_arbase)
        layout.addWidget(get_from_select_btn, 0, 2)

        target_mesh_names_label = QtWidgets.QLabel("target mesh names:")
        self.target_mesh_names_text = QtWidgets.QLineEdit()
        layout.addWidget(target_mesh_names_label, 1, 0)
        layout.addWidget(self.target_mesh_names_text, 1, 1)

        get_from_select_btn = QtWidgets.QPushButton("get from select")
        get_from_select_btn.clicked.connect(self.update_face_name)
        layout.addWidget(get_from_select_btn, 1, 2)

        create_btn = QtWidgets.QPushButton("create ARkit BS")
        create_btn.clicked.connect(self.create_ar52bs)
        layout.addWidget(create_btn, 2, 2)

        self.createnew_checkbox = QtWidgets.QCheckBox("create new")
        self.createnew_checkbox.setChecked(False)
        layout.addWidget(self.createnew_checkbox, 2, 1)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 设置窗口置顶

        self.show()

    def import_arbase(self):
        file_path = r"S:\Public\qiu_yi\JCQ_Tool\data\maya\iFacialMocapTestObj.ma"
        if cmds.objExists("allGrp"):
            print("allGrp already exists in the scene. Skipping import.")
            return
        cmds.file(file_path, i=True, type="mayaAscii", ignoreVersion=True, mergeNamespacesOnClash=False, namespace=":")

        # 隐藏导入的模型
        cmds.setAttr("allGrp" + ".visibility", False)
    def update_face_name(self):
        selection = cmds.ls(selection=True)  # 获取在 Maya 中选择的物

        if not selection:
            return

        mesh_names = ",".join(selection)  # 将物体名称用逗号连接起来
        self.target_mesh_names_text.setText(mesh_names)  # 将连接后的名称设置为文本输入框的文本

    # 创建 AR bs 52 按钮的回调函数
    def create_ar52bs(self, *args):

        arbsbasename = self.arkit_bs_name_text.text()
        headnames = self.target_mesh_names_text.text().split(",")

        checked = self.createnew_checkbox.isChecked()

        if not headnames or not arbsbasename:
            # 检查是否输入了目标网格名称和 AR bs 名称
            print("Please enter target mesh names and ar bs name")
            return

        bslist = cmds.listAttr(arbsbasename + ".w", m=True)

        if not bslist:
            # 检查是否找到了 AR bs 的属性列表
            print("No blendShape attributes found for " + arbsbasename)
            return
        for obj in headnames:
            cmds.createNode('transform', n=obj+'_AR_GP')
            if checked :
                cmds.duplicate(obj, n=obj+"_AR_base")
                cmds.parent(obj+"_AR_base", obj+'_AR_GP')
            new_bsname_list = []
            for i in range(len(bslist)):
                bsname = bslist[i]
                cmds.blendShape(arbsbasename, edit=True, w=[(i, 1)])

                cmds.duplicate(obj, n=obj+"_"+bsname)
                cmds.parent(obj+"_"+bsname, obj+'_AR_GP')
                cmds.setAttr(obj+"_"+bsname + ".visibility", 0)
                new_bsname_list.append(obj+"_"+bsname)

                cmds.blendShape(arbsbasename, edit=True, w=[(i, 0)])

            if checked :
                new_bsname_list.append(obj+"_AR_base")
            else:
                new_bsname_list.append(obj)

            cmds.blendShape(new_bsname_list, n=obj+"_AR52")
            for i in range(len(bslist)):
                try:
                    cmds.aliasAttr(bslist[i], '{}_AR52.w[{}]'.format(obj,i))
                except:
                    pass

# 创建 MR_Window 实例
myWindow = MR_Window()
