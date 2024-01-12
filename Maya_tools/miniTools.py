from PySide2 import QtWidgets, QtGui, QtCore



class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)
        self.setWindowTitle("mini tools")

        # 创建按钮
        button1 = QtWidgets.QPushButton("conbine tool", self)
        button1.clicked.connect(self.conbinetool)

        button2 = QtWidgets.QPushButton("conbine 2", self)
        button2.clicked.connect(self.conbinetool2)

        button3 = QtWidgets.QPushButton("按钮 3", self)
        button3.clicked.connect(self.button_clicked)

        button4 = QtWidgets.QPushButton("按钮 4", self)
        button4.clicked.connect(self.button_clicked)

        button5 = QtWidgets.QPushButton("按钮 5", self)
        button5.clicked.connect(self.button_clicked)

        button6 = QtWidgets.QPushButton("按钮 6", self)
        button6.clicked.connect(self.button_clicked)

        button7 = QtWidgets.QPushButton("按钮 7", self)
        button7.clicked.connect(self.button_clicked)

        button8 = QtWidgets.QPushButton("按钮 8", self)
        button8.clicked.connect(self.button_clicked)

        button9 = QtWidgets.QPushButton("按钮 9", self)
        button9.clicked.connect(self.button_clicked)

        button10 = QtWidgets.QPushButton("按钮 10", self)
        button10.clicked.connect(self.button_clicked)

        # 创建布局
        layout = QtWidgets.QGridLayout()
        layout.addWidget(button1, 0, 0)  # 第0行，第0列
        layout.addWidget(button2, 0, 1)  # 第0行，第1列
        layout.addWidget(button3, 1, 0)  # 第1行，第0列
        layout.addWidget(button4, 1, 1)  # 第1行，第1列
        layout.addWidget(button5, 2, 0)  # 第2行，第0列
        layout.addWidget(button6, 2, 1)  # 第2行，第1列
        layout.addWidget(button7, 3, 0)  # 第3行，第0列
        layout.addWidget(button8, 3, 1)  # 第3行，第1列
        layout.addWidget(button9, 4, 0)  # 第4行，第0列
        layout.addWidget(button10, 4, 1)  # 第4行，第1列

        self.setLayout(layout)
        self.resize(400, 300)  # 设置窗口的默认尺寸为宽度400和高度300
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 设置窗口置顶

        self.show()
    def conbinetool(self):
        # 获取当前选择的物体
        selection = cmds.ls(selection=True)
        if len(selection) < 2:
            cmds.warning("请选择两个以上物体！")
            return
        # 获取第一个物体的父级长名字
        try:
            parent_name = cmds.listRelatives(selection[0], parent=True, fullPath=True)[0]
        except:
            parent_name = False
        if parent_name:
            # 获取父级中的所有物体
            parent_objects = cmds.listRelatives(parent_name, children=True, fullPath=True)
            # 获取当前物体在父级列表中的位置
            index = parent_objects.index(parent_name + "|" + selection[0])
            combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

            split_group = parent_name.split("|")  # 将字符串按 "|" 分割成列表
            last_group = split_group[-1]  # 获取列表中的最后一个元素
            cmds.parent(combined_obj, last_group)

        else:
            # 获取父级中的所有物体
            parent_group = cmds.ls(assemblies=True)
            # 获取当前物体在父级列表中的位置
            index = parent_group.index(selection[0])
            combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

            last_group = parent_group
    def conbinetool2(self):
        # 获取当前选择的物体
        selection = cmds.ls(selection=True)
        selection_P = cmds.ls(selection=True, long=True)
        selection_P = selection_P[0].split("|")
        selection_P = selection_P[-2]

        if selection_P:

            # 获取父级中的所有物体
            parent_objects = cmds.listRelatives(selection_P, children=True, fullPath=True)
            print(parent_objects)
            # 获取当前物体在父级列表中的位置
            index = parent_objects.index("|" +selection_P + "|" + selection[0])
            combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

            split_group = selection_P.split("|")  # 将字符串按 "|" 分割成列表
            last_group = split_group[-1]  # 获取列表中的最后一个元素
            cmds.parent(combined_obj, last_group)

        else:
            # 获取父级中的所有物体
            parent_group = cmds.ls(assemblies=True)
            # 获取当前物体在父级列表中的位置
            index = parent_group.index(selection[0])
            combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

            last_group = parent_group
        # 移动第二个物体到第一个物体的后面
        cmds.reorder(combined_obj, front=True)
        cmds.reorder(combined_obj, relative=index)
        cmds.delete(selection[0])
        cmds.rename(combined_obj, selection[0][4:])

    def objrefresh(self):
        project_path = cmds.workspace(q=True, rootDirectory=True)
        # 获取当前选择的物体
        selection = cmds.ls(selection=True)
        for obj in selection:
            objname = obj
            file_path = project_path+"fix.obj"
            cmds.file(file_path, force=True, options="groups=0;ptgroups=0;materials=0;smoothing=1;normals=1", typ="OBJexport", es=True)
            # 获取第一个物体的父级长名字
            try:
                parent_name = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
            except:
                parent_name = False

            if parent_name:
                # 获取父级中的所有物体
                parent_objects = cmds.listRelatives(parent_name, children=True, fullPath=True)
                # 获取当前物体在父级列表中的位置
                index = parent_objects.index(parent_name + "|" + selection[0])
                combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

                split_group = parent_name.split("|")  # 将字符串按 "|" 分割成列表
                last_group = split_group[-1]  # 获取列表中的最后一个元素
                cmds.parent(combined_obj, last_group)

            else:
                # 获取父级中的所有物体
                parent_group = cmds.ls(assemblies=True)
                # 获取当前物体在父级列表中的位置
                index = parent_group.index(selection[0])
                combined_obj = cmds.polyUnite(selection, ch=False, mergeUVSets=True, centerPivot=True)[0]

                last_group = parent_group

        # 移动第二个物体到第一个物体的后面
        cmds.reorder(combined_obj, front=True)
        cmds.reorder(combined_obj, relative=index)
        cmds.rename(combined_obj, selection[0])
    def anymtoL(self):
        from maya import cmds
        import maya.mel as mel
        target = cmds.ls(sl=True)
        print(target)
        for t in target:
            if t.startswith("shader_"):
                newName = t + "hoge"
                tSG = cmds.listConnections(t + ".outColor", destination=True, plugs=True)
                tColorTex = []
                try:
                    tColorTex = cmds.listConnections(t + ".DiffuseTexture", source=True, plugs=True)
                except:
                    pass
                try:
                    cmds.rename(t, newName)
                except:
                    continue
                if tSG:
                    material = mel.eval('shadingNode -asShader -name ' + t + ' lambert')
                    cmds.connectAttr("%s.outColor" % material, tSG[0], f=True)
                if tColorTex:
                    cmds.connectAttr(tColorTex[0], "%s.color" % material, f=True)
                cmds.delete(newName)
    def button_clicked(self):
        button_text = self.sender().text()
        print(f"按钮 '{button_text}' 被点击！")


# 创建窗口实例
window = MyWindow()
