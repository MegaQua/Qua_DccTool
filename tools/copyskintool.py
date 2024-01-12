import maya.cmds as cmds
from PySide2 import QtWidgets, QtGui, QtCore

class SkinWeightCopier(QtWidgets.QWidget):
    def __init__(self):
        super(SkinWeightCopier, self).__init__(None)
        self.setWindowTitle("Batch Weight Copy Tool")

        # 创建按钮
        button = QtWidgets.QPushButton("Copy Skin Weights", self)
        button.clicked.connect(self.process_selected_objects)

        # 创建布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button)

        # 创建水平布局
        horizontal_layout = QtWidgets.QHBoxLayout()

        # 收集列表元素
        object_names = cmds.ls(selection=True)
        mid_index = len(object_names) // 2
        first_half = object_names[:mid_index]
        second_half = object_names[mid_index:]

        # 创建左上列表元素
        left_top_list = QtWidgets.QListWidget(self)
        for item in first_half:
            left_top_list.addItem(item)
        horizontal_layout.addWidget(left_top_list)

        # 创建箭头标签
        arrow_label = QtWidgets.QLabel(self)
        arrow_label.setText("➡")
        arrow_label.setStyleSheet("font-size: 24px;")
        horizontal_layout.addWidget(arrow_label)

        # 创建右上列表元素
        right_top_list = QtWidgets.QListWidget(self)
        for item in second_half:
            right_top_list.addItem(item)
        horizontal_layout.addWidget(right_top_list)

        layout.addLayout(horizontal_layout)

        # 创建按钮布局
        button_layout = QtWidgets.QHBoxLayout()

        # 创建靠左的按钮
        left_button = QtWidgets.QPushButton("skinCluster.envelope_SW", self)
        left_button.clicked.connect(self.switchEnvelope)
        button_layout.addWidget(left_button)

        # 在按钮布局中添加间距，使右侧按钮紧贴左侧按钮
        button_layout.addSpacing(10)

        # 创建右侧的按钮
        right_button = QtWidgets.QPushButton("reset dagpose", self)
        right_button.clicked.connect(self.resetdagpose)
        button_layout.addWidget(right_button)

        # 在按钮布局中添加间距，使右侧按钮和新按钮之间有一定间距
        button_layout.addSpacing(10)

        # 创建新的右侧按钮
        new_button = QtWidgets.QPushButton("New Button", self)
        button_layout.addWidget(new_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 设置窗口置顶

        self.show()
    def resetdagpose(self):
        # 通过type参数过滤出所有的dagPose节点
        dagpose_nodes = cmds.ls(type='dagPose')

        # 删除dagPose节点
        cmds.delete(dagpose_nodes)

        all_objects = cmds.ls()

        cmds.dagPose(all_objects, bindPose=True, save=True)
    def switchEnvelope(self):
        skin_clusters = cmds.ls(type="skinCluster")
        all_zero = True  # 检查所有envelope值是否已经为0

        for skin_cluster in skin_clusters:
            envelope_value = cmds.getAttr(skin_cluster + ".envelope")
            if envelope_value != 0:
                all_zero = False  # 如果有任何一个envelope值不为0，将all_zero标志设置为False
            cmds.setAttr(skin_cluster + ".envelope", 0)

        if all_zero:
            for skin_cluster in skin_clusters:
                cmds.setAttr(skin_cluster + ".envelope", 1)
    def copy_skin_weights(self, source, target):
        try:
            # 找到源对象的皮肤绑定节点
            skin_cluster = None
            history = cmds.listHistory(source)
            for node in history:
                if cmds.nodeType(node) == 'skinCluster':
                    skin_cluster = node
                    break

            # 获取源对象的骨骼列表
            joints = cmds.skinCluster(skin_cluster, q=True, inf=True)

            # 如果目标对象已经有皮肤绑定，删除它
            target_skin_cluster = None
            history = cmds.listHistory(target)
            for node in history:
                if cmds.nodeType(node) == 'skinCluster':
                    target_skin_cluster = node
                    break
            if target_skin_cluster:
                cmds.delete(target_skin_cluster)

            # 在目标对象上创建新的皮肤绑定节点
            cmds.skinCluster(joints, target, tsb=True)

            # 复制皮肤权重
            cmds.copySkinWeights(source, target, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='oneToOne')
        except:
            print("pass " + source + " and " + target)
    def process_selected_objects(self):
        selected_objects = cmds.ls(selection=True)
        # 判断选择的模型数量是否为2n个
        num_selected_objects = len(selected_objects)
        if num_selected_objects % 2 != 0:
            QtWidgets.QMessageBox.information(self, "Alert", "Please select an even number of models for operation.")
            #print("Please select an even number of models for operation.")
            return

        # 遍历n，以第i个对象和第2i个对象为参数，执行复制皮肤权重操作
        n = num_selected_objects // 2

        for i in range(n):
            source = selected_objects[i]
            target = selected_objects[i + n]
            self.copy_skin_weights(source, target)

# 示例用法
copier = SkinWeightCopier()

