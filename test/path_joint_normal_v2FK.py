from pyfbsdk import *
from PySide2 import QtWidgets, QtGui, QtCore


class MB_jointPath_tool(QtWidgets.QWidget):
    def __init__(self):
        self.GPJoint = ["tentacleA1","tentacleB1","tentacleC1","tentacleD1","tentacleE1","tentacleF1"]
        self.childRoot = ["tentacleABa_1","tentacleBBa_1","tentacleCBa_1","tentacleDBa_1","tentacleEBa_1","tentacleFBa_1"]
        self.name = "rigA"
        self.conNum = 10
        self.MarkerSize = 1000
        self.Active = False
        #super().__init__()
        #self.setWindowTitle("MB_jointPath_tool")

        #layout = QtWidgets.QGridLayout(self)
        # 第一行
        #target_name_label = QtWidgets.QLabel("target name")
        #layout.addWidget(target_name_label, 0, 0)

        # 为所有按钮连接临时函数
        # set_selection_text_btn.clicked.connect(self.get_from_selection)

        # 设置窗口置顶
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        # self.show()

    def collect_all_joints(self, start_joint_name):
        # 查找场景中的起始关节
        start_joint = FBFindModelByLabelName(start_joint_name)
        if not start_joint:
            return [False]  # 如果没有找到起始关节，返回只包含False的列表

        # 初始化用于存储关节对象的列表
        joints_list = []

        # 当前关节设为起始关节
        current_joint = start_joint

        # 循环遍历直到没有更多子关节或遇到多个子关节的关节
        while current_joint:
            # 将当前关节添加到列表中
            joints_list.append(current_joint)

            # 检查当前关节的子关节数量
            if len(current_joint.Children) > 1:
                # 如果子关节超过一个，返回只包含False的列表
                return [False]

            # 移动到下一个子关节，如果有的话
            current_joint = current_joint.Children[0] if current_joint.Children else None

        return joints_list

    def createEndNull(self, jointList):
        if len(jointList) < 2:
            raise ValueError("至少需要两个关节来确定方向")

        # 获取倒数第二个关节和最后一个关节的全局位置
        second_last_joint_position = self.get_global_position(jointList[-2])
        last_joint_position = self.get_global_position(jointList[-1])

        # 计算方向向量（从倒数第二个关节指向最后一个关节）
        direction = [
            last_joint_position[0] - second_last_joint_position[0],
            last_joint_position[1] - second_last_joint_position[1],
            last_joint_position[2] - second_last_joint_position[2]
        ]

        # 假设新点与最后一个关节的距离与最后两个关节之间的距离相同
        new_point_position = FBVector3d(
            last_joint_position[0] + direction[0],
            last_joint_position[1] + direction[1],
            last_joint_position[2] + direction[2]
        )

        # 创建一个新的空对象（null）
        jointEnd = FBModelNull(self.name + "_JointEnd")
        jointEnd.Show = False  # 确保新创建的对象是隐藏的
        jointEnd.SetVector(new_point_position)  # 设置新对象的位置

        return jointEnd

    def getConstraintByName(self, Name):
        lConstraints = FBSystem().Scene.Constraints  # 获取当前场景中的所有约束列表
        for each in lConstraints:  # 遍历场景中的所有约束
            if each.Name == Name:  # 检查约束名称是否匹配
                return each  # 如果找到匹配的约束，立即返回它
            else:
                return None

    def getRelationByName(self, RelationName):
        lConstraints = FBSystem().Scene.Constraints  # 获取当前场景中的所有约束列表
        for each in lConstraints:  # 遍历场景中的所有约束
            if each.Name == RelationName:  # 检查约束名称是否匹配
                return each  # 如果找到匹配的约束，立即返回它

        # 如果遍历完成后没有找到匹配的约束，则创建一个新的约束
        return FBConstraintRelation(RelationName)  # 创建一个新的约束并返回

    def get_global_position(self, target):
        # 创建一个FBMatrix对象来接收变换矩阵
        matrix = FBMatrix()
        # 获取对象的全局变换矩阵
        target.GetMatrix(matrix)
        # 提取全局坐标
        # 矩阵的最后一列的前三个元素代表X, Y, Z全局坐标
        global_position = FBVector3d(matrix[12], matrix[13], matrix[14])

        return global_position

    def create_curve(self, target_list, curve_name):
        curve = FBModelPath3D(self.name + "_" + curve_name + "_curve")
        curve.Show = True
        curve.Visible = True
        for obj in target_list:
            vec3d = self.get_global_position(obj)
            vec4d = FBVector4d(vec3d[0], vec3d[1], vec3d[2], 1.0)
            curve.PathKeyEndAdd(vec4d)
        curve.PathKeyRemove(0)
        curve.PathKeyRemove(0)
        return curve

    def interpolate_points_3d(self, point1, point2, n):
        """
        输入两个点的坐标和一个常数n，将两点构成的直线分为n-1份，返回点坐标列表。

        :param point1: 第一个点的坐标，元组形式 (x1, y1, z1)
        :param point2: 第二个点的坐标，元组形式 (x2, y2, z2)
        :param n: 划分的份数，必须至少为2
        :return: 点坐标列表，包含 n 个元素
        """
        # 解构输入点的坐标
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        # 检查 n 是否大于 1
        if n < 2:
            raise ValueError("n must be at least 2 to include both endpoints.")

        # 初始化点列表，包括起始点
        points = [point1]

        # 计算每个维度上的增量
        dx = (x2 - x1) / (n - 1)
        dy = (y2 - y1) / (n - 1)
        dz = (z2 - z1) / (n - 1)

        # 生成中间点
        for i in range(1, n - 1):
            new_x = x1 + i * dx
            new_y = y1 + i * dy
            new_z = z1 + i * dz
            points.append((new_x, new_y, new_z))

        # 添加结束点
        points.append(point2)

        return points

    def connectObjToCurve(self, objList, Curve):
        for index, obj in enumerate(objList):
            Curve.PathKeySetControlNode(index, obj)

    def create_offset(self, model):
        # 创建 offset 对象的名称

        offset = FBModelNull(model.Name + "_offset")  # 创建 offset 对象

        # 获取 model 的全局变换矩阵并应用到 offset
        matrix = FBMatrix()
        model.GetMatrix(matrix)
        offset.SetMatrix(matrix)

        # 将 model 设置为 offset 的子对象
        model.Parent = offset

        return offset

    def create_dummys(self, models, dummytype="offset", dummylook="null", name="Location", offset=(0, 0, 0), color=FBColor(1.0, 1.0, 1.0),
                      P=False):
        """
        创建虚拟对象（dummy）并根据指定类型设置其父子关系和外观。

        参数:
        models (list): 包含目标对象或位置的列表，可以是 FBModel 或 FBVector3d 对象。
        dummytype (str, 可选): 虚拟对象类型，可以是 "offset", "child" 或 "copy"。默认为 "offset"。
        dummylook (str, 可选): 虚拟对象的外观，可以是 "null", "HardCross", "LightCross", "Cube", "Sphere", 或 "Capsule"。默认为 "null"。
        name (str, 可选): 如果目标是 FBVector3d 对象，虚拟对象的名称前缀。默认为 "Location"。
        offset (tuple, 可选): 虚拟对象的位置偏移量，格式为 (x_offset, y_offset, z_offset)。默认为 (0, 0, 0)。
        color (FBColor, 可选): 标记对象的颜色。默认为 FBColor(1.0, 1.0, 1.0)。
        enable_yoffset_chain (bool, 可选): 是否启用 yoffset 链接。默认为 False。

        返回:
        list: 创建的虚拟对象列表。

        功能:
        该函数根据输入的目标对象列表（models），为每个对象创建一个虚拟对象（dummy）。可以指定虚拟对象的类型、外观和位置偏移量。虚拟对象的父子关系将根据 dummytype 设置。
        """

        def create_dummy(target, dummytype, dummylook, name, offset, color):
            x_offset, y_offset, z_offset = offset
            if isinstance(target, FBVector3d):
                global_position = target
                target_name = name
                use_global_position = True
            else:
                target_name = target.Name + f"_{dummytype}"
                use_global_position = False

            if dummylook == "HardCross":
                dummy = FBModelMarker(target_name)
                dummy.Look = FBMarkerLook.kFBMarkerLookHardCross
                dummy.Show = True
            elif dummylook == "LightCross":
                dummy = FBModelMarker(target_name)
                dummy.Look = FBMarkerLook.kFBMarkerLookLightCross
                dummy.Show = True
            elif dummylook == "Cube":
                dummy = FBModelMarker(target_name)
                dummy.Look = FBMarkerLook.kFBMarkerLookCube
                dummy.Show = True
            elif dummylook == "Sphere":
                dummy = FBModelMarker(target_name)
                dummy.Look = FBMarkerLook.kFBMarkerLookSphere
                dummy.Show = True
            elif dummylook == "Capsule":
                dummy = FBModelMarker(target_name)
                dummy.Look = FBMarkerLook.kFBMarkerLookCapsule
                dummy.Show = True
            else:
                dummy = FBModelNull(target_name)

            if isinstance(dummy, FBModelMarker):
                dummy.Size = self.MarkerSize  # 设置Marker的大小
                dummy.Color = color  # 设置Marker的颜色

            if use_global_position:
                dummy.Translation = FBVector3d(global_position[0] + x_offset, global_position[1] + y_offset, global_position[2] + z_offset)
            else:
                matrix = FBMatrix()
                target.GetMatrix(matrix)
                matrix[12] += x_offset
                matrix[13] += y_offset
                matrix[14] += z_offset
                dummy.SetMatrix(matrix)

            if dummytype == "offset":
                target.Parent = dummy
            elif dummytype == "child":
                dummy.Parent = target
            # 若 dummytype 为 "copy"，无需更改 parent-child 关系

            return dummy

        dummylist = []
        for target in models:
            dummylist.append(create_dummy(target, dummytype, dummylook, name, offset, color))

        if P:
            for i in range(len(dummylist) - 1):
                dummylist[i + 1].Parent = dummylist[i]

        return dummylist

    def interpolate_between_first_and_last(self, models, num_points, nonlinear=False):
        """
        在第一个和最后一个模型之间插值计算点的坐标。

        参数:
        models (list): FBModel对象列表。
        num_points (int): 分段后的点数，包括起点和终点。
        nonlinear (bool): 是否开启非线性插值功能，默认为关闭。

        返回:
        list: 包含插值后点的FBVector3d对象列表。
        """

        # 获取第一个和最后一个模型的全局位置
        start_point = self.get_global_position(models[0])
        end_point = self.get_global_position(models[-1])
        new_points = []

        if num_points < 2:
            raise ValueError("分段点数必须至少为2")

        # 添加起点
        new_points.append(FBVector3d(start_point[0], start_point[1], start_point[2]))

        # 计算每段的长度
        total_length = num_points - 1
        for i in range(1, total_length):
            if nonlinear:
                t = 1 - ((total_length - i) / total_length) ** 2  # 使用反向指数插值，使得越靠近末端点越密集
            else:
                t = i / total_length  # 使用线性插值
            interpolated_point = FBVector3d(
                start_point[0] + (end_point[0] - start_point[0]) * t,
                start_point[1] + (end_point[1] - start_point[1]) * t,
                start_point[2] + (end_point[2] - start_point[2]) * t
            )
            new_points.append(interpolated_point)

        # 添加终点
        new_points.append(FBVector3d(end_point[0], end_point[1], end_point[2]))

        return new_points

    def interpolate_points_simple(self, models, num_points):
        points = [self.get_global_position(model) for model in models]  # 获取每个模型的全局位置
        segments = num_points - 1  # 总共需要分的段数
        segment_length = len(points) - 1  # 原始点间的段数
        points_per_segment = segment_length // segments  # 每个新分段包含的原始点段数
        new_points = [points[0]]  # 开始点

        current_index = 0
        for i in range(1, segments):
            # 计算当前段的终点
            current_index += points_per_segment
            if current_index >= len(points) - 1:
                break
            # 选择当前段的中点
            midpoint_index = current_index + points_per_segment // 2
            if midpoint_index >= len(points):
                midpoint_index = len(points) - 1

            # 确保midpoint_index不超出范围
            midpoint_index = min(midpoint_index, len(points) - 1)

            new_points.append(points[midpoint_index])

        new_points.append(points[-1])  # 结束点

        # 将坐标转换为FBVector3d对象列表
        new_vector3d_points = [FBVector3d(point[0], point[1], point[2]) for point in new_points]

        return new_vector3d_points

    def conCreate(self, start, end):
        start = self.get_global_position(start)
        end = self.get_global_position(end)
        coordinates = self.interpolate_points_3d(start, end, self.conNum)
        ConList = []
        for idx, (x, y, z) in enumerate(coordinates):
            # 创建一个新的 Locator
            locator = FBModelMarker(self.name + "_Con_{}".format(idx))
            locator.Look = FBMarkerLook.kFBMarkerLookHardCross  # 设置Locator的外观为十字形
            locator.Show = True  # 确保Locator是可见的
            locator.Translation = FBVector3d(x, y, z)  # 设置Locator的位置
            ConList.append(locator)
        return ConList

    def create_Marker(self, input_obj, name, color=None):
        # 检查输入是否为FBVector3d，如果不是，则获取全球坐标
        if not isinstance(input_obj, FBVector3d):
            global_position = self.get_global_position(input_obj)
        else:
            global_position = input_obj

        # 如果未指定颜色，使用默认的红色
        if color is None:
            color = FBColor(1.0, 0.0, 0.0)  # 红色

        # 创建一个新的 Locator
        locator = FBModelMarker(self.name + "_" + name + "_Marker")
        locator.Look = FBMarkerLook.kFBMarkerLookHardCross  # 设置Locator的外观为十字形
        locator.Show = True  # 确保Locator是可见的
        locator.Size = self.MarketSize  # 设置Locator的大小
        locator.Color = color  # 设置Locator的颜色
        locator.Translation = FBVector3d(global_position[0], global_position[1], global_position[2])  # 设置Locator的位置
        return locator

    def create_curve_Cons(self, jointlist, num, y_offset=0):

        conlist = []
        interpolate_points_list = self.interpolate_points_simple(jointlist, num)

        for index, point in enumerate(interpolate_points_list):
            # point[1] += y_offset
            # print(point)
            marker = self.create_Marker(point, str(index + 1), FBColor(1.0, 1.0, 0))  # 使用点的坐标来创建Locator
            if y_offset:
                marker.Translation = FBVector3d(point[0], point[1] + y_offset, point[2])
            conlist.append(marker)
        return conlist

    def creat_Cons_offset(self, conlist):
        offsetlist = []
        for con in conlist:
            offsetlist.append(self.create_offset(con))
        return offsetlist

    def create_chain_offsets(self, obj_list):
        def create_offset(model):
            # 创建 offset 对象的名称
            offset = FBModelNull(model.Name + "_offset")  # 创建 offset 对象

            # 获取 model 的全局变换矩阵并应用到 offset
            matrix = FBMatrix()
            model.GetMatrix(matrix)
            offset.SetMatrix(matrix)

            return offset

        # 检查是否至少有一个对象
        if not obj_list:
            return []

        offset_list = []

        for i in range(len(obj_list)):
            offset = create_offset(obj_list[i])
            offset_list.append(offset)

            if i > 0:
                offset_list[i].Parent = offset_list[i - 1]  # 将当前 offset 设置为前一个 offset 的子对象

        return offset_list

    def calculate_relative_distances(self, objects):

        # 辅助函数计算两点之间的欧几里得距离
        def distance(p1, p2):
            return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) ** 0.5

        # 获取对象的全局位置
        points = [self.get_global_position(obj) for obj in objects]

        # 计算线段的总长度
        total_length = 0
        distances = [0]  # 初始化距离列表，第一个点的距离为0
        for i in range(1, len(points)):
            dist = distance(points[i - 1], points[i])
            total_length += dist
            distances.append(total_length)  # 存储每个点的累计距离

        # 标准化距离以获取相对于总长度的位置
        normalized_distances = [d / total_length * 1 for d in distances]

        return normalized_distances

    def createPathConstrain(self, target, curve):
        # 获取约束管理器
        constraint_manager = FBConstraintManager()
        # 创建路径约束
        path_constraint = constraint_manager.TypeCreateConstraint("Path")
        # 将目标物体添加到约束的源列表
        path_constraint.ReferenceAdd(0, target)
        # 将曲线添加到约束的目标列表
        path_constraint.ReferenceAdd(1, curve)
        path_constraint.Name = target.Name + "_Path"
        # 激活约束
        path_constraint.Active = self.Active
        return path_constraint

    def createPathConstrain_s(self, target_list, curve):
        Paths = []
        for i in target_list:
            path = self.createPathConstrain(i, curve)
            Paths.append(path)
        return Paths

    def pathconect(self, Relation, Path, NUM):
        path1Source = testRelation.SetAsSource(path1)
        path2Source = testRelation.ConstrainObject(path2)

    def pathRolation(self, TargetList, PathList):
        def Find_AnimationNode(pParent, pName):
            # Boxが指定された名前のノードを持っているかを調べる。
            lResult = None
            for lNode in pParent.Nodes:
                if lNode.Name == pName:
                    lResult = lNode
                    break
            return lResult

        Relation = FBConstraintRelation(PathList[-1].Name + "_Relation")
        mainPath = PathList[-1]
        NUMS = self.calculate_relative_distances(TargetList)
        mainPathSender = Relation.SetAsSource(mainPath)
        # Relation.SetBoxPosition(mainPathSender, 0, 0)
        mainPathSender_warp = Find_AnimationNode(mainPathSender.AnimationNodeOutGet(), 'Warp')
        for idx, (Path, NUM) in enumerate(zip(PathList[:-1], NUMS[:-1])):
            receiver = Relation.ConstrainObject(Path)
            receiver_warp = Find_AnimationNode(receiver.AnimationNodeInGet(), 'Warp')
            Multiply = Relation.CreateFunctionBox("Number", "Multiply (a x b)")
            a = Find_AnimationNode(Multiply.AnimationNodeInGet(), 'a')
            b = Find_AnimationNode(Multiply.AnimationNodeInGet(), 'b')
            Result = Find_AnimationNode(Multiply.AnimationNodeOutGet(), 'Result')
            b.WriteData([float(NUM)])
            FBConnect(mainPathSender_warp, a)
            FBConnect(Result, receiver_warp)

            Relation.SetBoxPosition(Multiply, 400, idx * 200)
            Relation.SetBoxPosition(receiver, 800, idx * 200)

        return Relation, mainPath

    def warppathtogether(self, Relation, mainPath, OffsetmainPath):
        def Find_AnimationNode(pParent, pName):
            # Boxが指定された名前のノードを持っているかを調べる。
            lResult = None
            for lNode in pParent.Nodes:
                if lNode.Name == pName:
                    lResult = lNode
                    break
            return lResult

        Sender = Relation.SetAsSource(mainPath)
        Sender_warp = Find_AnimationNode(Sender.AnimationNodeOutGet(), 'Warp')
        receiver = Relation.ConstrainObject(OffsetmainPath)
        receiver_warp = Find_AnimationNode(receiver.AnimationNodeInGet(), 'Warp')
        FBConnect(Sender_warp, receiver_warp)

    def createChainAim(self, CPlist, UpList=None):
        def create_aim(child, parent, world_up_object=None):
            constraint_manager = FBConstraintManager()
            Aim = constraint_manager.TypeCreateConstraint("Aim")
            Aim.ReferenceAdd(0, child)
            Aim.ReferenceAdd(1, parent)
            if world_up_object is not None:
                Aim.ReferenceAdd(2, world_up_object)
                Aim.PropertyList.Find('World Up Type').Data = 1
            Aim.Name = child.Name + "_" + parent.Name + "_Aim"
            Aim.Active = self.Active
            return Aim

        aims = []
        for i in range(len(CPlist) - 1):
            child = CPlist[i]
            parent = CPlist[i + 1]
            world_up_object = UpList[i] if UpList is not None else None
            aim_constraint = create_aim(child, parent, world_up_object)
            aims.append(aim_constraint)

        return aims

    def create_parent(self, child, parent):
        constraint_manager = FBConstraintManager()
        parent_constraint = constraint_manager.TypeCreateConstraint("Parent/Child")
        parent_constraint.ReferenceAdd(0, child)
        parent_constraint.ReferenceAdd(1, parent)
        parent_constraint.Name = f"{child.Name}_{parent.Name}_Parent/Child"
        parent_constraint.PropertyList.Find('AffectScalingX').Data = 1
        parent_constraint.PropertyList.Find('AffectScalingY').Data = 1
        parent_constraint.PropertyList.Find('AffectScalingZ').Data = 1
        parent_constraint.Active = self.Active
        return parent_constraint

    def jointchain_parent(self, Childs, Parents):
        def create_parent(child, parent):
            constraint_manager = FBConstraintManager()
            parent_constraint = constraint_manager.TypeCreateConstraint("Parent/Child")
            parent_constraint.ReferenceAdd(0, child)
            parent_constraint.ReferenceAdd(1, parent)
            parent_constraint.Name = f"{child.Name}_{parent.Name}_Parent/Child"
            parent_constraint.PropertyList.Find('AffectScalingX').Data = 1
            parent_constraint.PropertyList.Find('AffectScalingY').Data = 1
            parent_constraint.PropertyList.Find('AffectScalingZ').Data = 1
            parent_constraint.Active = self.Active
            return parent_constraint

        constraints = []
        for child, parent in zip(Childs, Parents):
            constraint = create_parent(child, parent)
            constraints.append(constraint)

        return constraints

    def Transformation_lock(self, targetlist, attr="all"):
        """
        锁定目标对象的指定变换属性。

        参数:
        targetlist (list): 需要锁定属性的目标对象列表。
        attr (str, 可选): 要锁定的属性，可以是 "all", "tx", "r", "sz" 或组合，例如 "tyz", "tx,r,sz" 等。默认为 "all"。
        """
        # 属性索引字典
        attr_dict = {
            "t": ("Lcl Translation", [0, 1, 2]),
            "r": ("Lcl Rotation", [0, 1, 2]),
            "s": ("Lcl Scaling", [0, 1, 2])
        }

        # 根据后续字母确定要锁定的轴
        axis_dict = {
            "x": [0],
            "y": [1],
            "z": [2],
            "xy": [0, 1],
            "xz": [0, 2],
            "yz": [1, 2],
            "xyz": [0, 1, 2]
        }

        lock_attrs = []

        # 解析 attr 参数
        if attr == "all":
            lock_attrs = [("Lcl Translation", [0, 1, 2]), ("Lcl Rotation", [0, 1, 2]), ("Lcl Scaling", [0, 1, 2])]
        else:
            attr_list = attr.split(",")
            for a in attr_list:
                i = 0
                while i < len(a):
                    type_char = a[i]
                    if type_char in attr_dict:
                        prop_name, default_indices = attr_dict[type_char]
                        j = i + 1
                        while j < len(a) and a[j] not in attr_dict:
                            j += 1
                        axis_str = a[i + 1:j]
                        indices = axis_dict.get(axis_str, default_indices)
                        lock_attrs.append((prop_name, indices))
                        i = j
                    else:
                        raise ValueError(f"Invalid attribute type: {type_char}")

        # 锁定属性
        for target in targetlist:
            for prop_name, indices in lock_attrs:
                prop = target.PropertyList.Find(prop_name)
                if prop:
                    for index in indices:
                        prop.SetMemberLocked(index, True)

    def createChainScale(self, Clist, YList,ZList):
        def Find_AnimationNode(pParent, pName):
            # Boxが指定された名前のノードを持っているかを調べる。
            lResult = None
            for lNode in pParent.Nodes:
                if lNode.Name == pName:
                    lResult = lNode
                    break
            return lResult

        def calculate_distance_between_models(model1, model2):
            def get_world_position(model):
                matrix = FBMatrix()
                model.GetMatrix(matrix, FBModelTransformationType.kModelTransformation, True, None)
                world_position = FBVector3d(matrix[12], matrix[13], matrix[14])
                return world_position
            position1 = get_world_position(model1)
            position2 = get_world_position(model2)

            dx = position2[0] - position1[0]
            dy = position2[1] - position1[1]
            dz = position2[2] - position1[2]

            distance = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
            return distance

        distance =calculate_distance_between_models(Clist[0],Clist[1])
        #print(distance)
        Relation = FBConstraintRelation(self.name + "_scale_Relation")

        Divide = Relation.CreateFunctionBox("Number", "Divide (a/b)")
        a = Find_AnimationNode(Divide.AnimationNodeInGet(), 'a')
        b = Find_AnimationNode(Divide.AnimationNodeInGet(), 'b')
        Divide_Result = Find_AnimationNode(Divide.AnimationNodeOutGet(), 'Result')
        b.WriteData([distance])

        Distance3 = Relation.CreateFunctionBox("Vector", "Distance")
        Distance3_v1 = Find_AnimationNode(Distance3.AnimationNodeInGet(), 'v1 (Position)')
        Distance3_v2 = Find_AnimationNode(Distance3.AnimationNodeInGet(), 'v2 (Position)')
        Distance3_result = Find_AnimationNode(Distance3.AnimationNodeOutGet(), 'Result')

        Distance_Sender1 = Relation.SetAsSource(Clist[0])
        Distance_Sender1_Translation = Find_AnimationNode(Distance_Sender1.AnimationNodeOutGet(), 'Translation')
        Distance_Sender2 = Relation.SetAsSource(Clist[1])
        Distance_Sender2_Translation = Find_AnimationNode(Distance_Sender2.AnimationNodeOutGet(), 'Translation')

        FBConnect(Distance_Sender1_Translation, Distance3_v1)
        FBConnect(Distance_Sender2_Translation, Distance3_v2)
        FBConnect(Distance3_result, a)

        Relation.SetBoxPosition(Distance_Sender1, -400, -200)
        Relation.SetBoxPosition(Distance_Sender2, -400, -140)
        Relation.SetBoxPosition(Distance3, 0, -200)
        Relation.SetBoxPosition(Divide, 400, -200)

        for idx, (child, Y , Z) in enumerate(zip(Clist, YList,ZList)):
            Sender1 = Relation.SetAsSource(child)
            receiver1 = Relation.ConstrainObject(child)
            Sender2 = Relation.SetAsSource(Y)
            Sender3 = Relation.SetAsSource(Z)
            Sender1_Translation = Find_AnimationNode(Sender1.AnimationNodeOutGet(), 'Translation')
            Sender2_Translation = Find_AnimationNode(Sender2.AnimationNodeOutGet(), 'Translation')
            Sender3_Translation = Find_AnimationNode(Sender3.AnimationNodeOutGet(), 'Translation')
            receiver1_Scaling = Find_AnimationNode(receiver1.AnimationNodeInGet(), 'Scaling')

            Distance1 = Relation.CreateFunctionBox("Vector", "Distance")
            Distance1_v1 = Find_AnimationNode(Distance1.AnimationNodeInGet(), 'v1 (Position)')
            Distance1_v2 = Find_AnimationNode(Distance1.AnimationNodeInGet(), 'v2 (Position)')
            Distance1_result = Find_AnimationNode(Distance1.AnimationNodeOutGet(), 'Result')

            Distance2 = Relation.CreateFunctionBox("Vector", "Distance")
            Distance2_v1 = Find_AnimationNode(Distance2.AnimationNodeInGet(), 'v1 (Position)')
            Distance2_v2 = Find_AnimationNode(Distance2.AnimationNodeInGet(), 'v2 (Position)')
            Distance2_result = Find_AnimationNode(Distance2.AnimationNodeOutGet(), 'Result')

            Vector_to_Number = Relation.CreateFunctionBox('Converters', 'Number to Vector')
            Vector_to_Number_X = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'X')

            #Vector_to_Number_X.WriteData([1])
            FBConnect(Divide_Result, Vector_to_Number_X)

            Vector_to_Number_Y = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'Y')
            Vector_to_Number_Z = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'Z')
            Vector_to_Number_result = Find_AnimationNode(Vector_to_Number.AnimationNodeOutGet(), 'Result')

            FBConnect(Sender1_Translation, Distance1_v1)
            FBConnect(Sender2_Translation, Distance1_v2)

            FBConnect(Sender1_Translation, Distance2_v1)
            FBConnect(Sender3_Translation, Distance2_v2)
            #FBConnect(Distance_result, Vector_to_Number_X)
            FBConnect(Distance1_result, Vector_to_Number_Y)
            FBConnect(Distance2_result, Vector_to_Number_Z)
            FBConnect(Vector_to_Number_result, receiver1_Scaling)

            Relation.SetBoxPosition(Sender1, 0, idx * 200)
            Relation.SetBoxPosition(receiver1, 1200, idx * 200)
            Relation.SetBoxPosition(Sender2, 0, idx * 200 + 60)
            Relation.SetBoxPosition(Sender3, 0, idx * 200 + 120)
            Relation.SetBoxPosition(Distance1, 400, idx * 200)
            Relation.SetBoxPosition(Distance2, 400, idx * 200+ 60)
            Relation.SetBoxPosition(Vector_to_Number, 800, idx * 200)
    def one_chain_RS(self,joints):
        joints_copy = self.create_dummys(joints, dummytype="copy")
        self.jointchain_parent(joints,joints_copy)
        joints_copy.append(self.createEndNull(joints_copy))
        for i in range(len(joints_copy) - 1):
            joints_copy[i + 1].Parent = joints_copy[i]

        Cons_location = self.interpolate_between_first_and_last(joints_copy, self.conNum)
        Cons = self.create_dummys(Cons_location, dummytype="copy", name=self.name + "_con 1", dummylook="HardCross")
        Cons_offset = self.create_dummys(Cons)
        PathCurve = self.create_curve(Cons, "Con")

        Y_Cons = self.create_dummys(Cons, dummytype="Y", offset=(0, 1, 0))
        for i in range(len(Cons)):
            Y_Cons[i].Parent = Cons[i]
        Y_PathCurve = self.create_curve(Y_Cons, "Cons_Y")
        joints_copy_yoffset = self.create_dummys(joints_copy, dummytype="Y", offset=(0, 1, 0),P=True)

        Z_Cons = self.create_dummys(Cons, dummytype="Z", offset=(0, 0, 1))
        for i in range(len(Cons)):
            Z_Cons[i].Parent = Cons[i]
        Z_PathCurve = self.create_curve(Z_Cons, "Cons_Z")
        joints_copy_zoffset = self.create_dummys(joints_copy, dummytype="Z", offset=(0, 0, 1),P=True)

        JointPaths = self.createPathConstrain_s(joints_copy, PathCurve)
        Y_JointPaths = self.createPathConstrain_s(joints_copy_yoffset, Y_PathCurve)
        Z_JointPaths = self.createPathConstrain_s(joints_copy_zoffset, Z_PathCurve)

        Relation, mainPath = self.pathRolation(joints_copy, JointPaths)
        _, Y_OffsetmainPath = self.pathRolation(joints_copy_yoffset, Y_JointPaths)
        _, Z_OffsetmainPath = self.pathRolation(joints_copy_yoffset, Z_JointPaths)
        self.warppathtogether(Relation, mainPath, Y_OffsetmainPath)
        self.warppathtogether(Relation, mainPath, Z_OffsetmainPath)

        self.createChainAim(joints_copy, joints_copy_yoffset)
        self.createChainScale(joints_copy, joints_copy_yoffset,joints_copy_zoffset)

        self.Transformation_lock(joints_copy)
        self.Transformation_lock(Cons_offset)
        self.Transformation_lock(joints_copy_yoffset)
        self.Transformation_lock(joints_copy_zoffset)
        self.Transformation_lock(Y_Cons)
        self.Transformation_lock(Z_Cons)
        self.Transformation_lock(Cons,"ryz,sx")
        #self.connectObjToCurve(Cons,PathCurve)
    def main(self):
        for name in self.GPJoint:

            joints_base = self.collect_all_joints(name)

            jointsCons = self.create_dummys(joints_base, dummytype="jointCon", dummylook="HardCross")
            self.jointchain_parent(joints_base, jointsCons)

            jointsConsOffsets = self.create_dummys(jointsCons)
            for i in range(1, len(jointsConsOffsets)):
                jointsConsOffsets[i].Parent = jointsCons[i - 1]




main = MB_jointPath_tool()
main.main()