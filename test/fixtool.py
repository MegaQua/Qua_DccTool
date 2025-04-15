from pyfbsdk import *
from PySide2 import QtWidgets, QtGui, QtCore
import re


# 执行
# 函数 名称指定
class Fix_tool(QtWidgets.QWidget):
    def __init__(self):
        self.rootJoint = "Arm01"
        self.childRoot = ["fingerA1", "fingerB1", "fingerC1", "fingerD1", "fingerE1", "fingerF1"]
        self.name = "rig"
        self.conNum = 10
        self.MarkerSize = 5000
        self.Active = False
        # super().__init__()
        # self.setWindowTitle("MB_jointPath_tool")

        # layout = QtWidgets.QGridLayout(self)
        # 第一行
        # target_name_label = QtWidgets.QLabel("target name")
        # layout.addWidget(target_name_label, 0, 0)

        # 为所有按钮连接临时函数
        # set_selection_text_btn.clicked.connect(self.get_from_selection)

        # 设置窗口置顶
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        # self.show()

    def classify_null_objects_by_relation(self, relation_long_name):
        """
        根据给定的长名字的命名空间，查找场景中的 null 对象，并按指定条件分类到三个列表。

        参数:
        relation_long_name (str): 用于匹配的长名字，获取命名空间前缀。

        返回:
        三个列表，分别是符合指定条件的 'Y', 'Z' 和 'C' 对象列表。
        """
        # 提取命名空间前缀（以 ":" 分隔的部分）
        namespace = relation_long_name.split(":")[0] if ":" in relation_long_name else ""

        # 定义三个列表来容纳符合条件的对象
        y_objects = []
        z_objects = []
        fkcon_offset_objects = []

        # 如果命名空间中包含 "enm"，则只匹配 _main_offset_Y 和 _main_offset_Z 的特征
        if "enm" in namespace:
            y_pattern = re.compile(f"^{namespace}.*?_main_offset_Y$", re.IGNORECASE)
            z_pattern = re.compile(f"^{namespace}.*?_main_offset_Z$", re.IGNORECASE)
            fkcon_offset_pattern = re.compile(f"^{namespace}.*?_main_offset$", re.IGNORECASE)
        else:
            # 检查 relation_long_name 中是否包含 "U_scale_Relation" 或 "L_scale_Relation"，并设置前缀
            if "Center" in relation_long_name:
                prefix = "Center"
            elif "U_scale_Relation" in relation_long_name:
                prefix = "U"
            elif "L_scale_Relation" in relation_long_name:
                prefix = "L"
            else:
                prefix = ""

            # 正则表达式匹配模式，确保名称不包含 "rig" 和 "Cuvre"，并匹配指定前缀条件
            y_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_Y)$", re.IGNORECASE)
            z_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_Z)$", re.IGNORECASE)
            fkcon_offset_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_FKcon_offset)$", re.IGNORECASE)

        # 遍历场景中的所有 FBModelNull 对象
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelNull):
                obj_name = obj.LongName

                # 根据名字匹配条件，将对象添加到相应列表
                if y_pattern.match(obj_name):
                    y_objects.append(obj)
                elif z_pattern.match(obj_name):
                    z_objects.append(obj)
                elif fkcon_offset_pattern.match(obj_name):
                    fkcon_offset_objects.append(obj)

        # 返回三个独立的列表
        return y_objects, z_objects, fkcon_offset_objects
    def clear_boxes_by_relation_name(self, relation_name):
        """
        根据给定的名称查找 FBConstraintRelation 对象并清除其中的所有 Box。

        参数:
        relation_name (str): 要清除 Box 的 FBConstraintRelation 对象的名称。
        """
        # 查找指定名称的 FBConstraintRelation 对象
        constraint_relation = None
        for obj in FBSystem().Scene.Constraints:
            if isinstance(obj, FBConstraintRelation) and obj.LongName == relation_name:
                constraint_relation = obj
                break

        # 如果找到对象，清除其中的所有 Box
        if constraint_relation:
            boxes_to_delete = [box for box in constraint_relation.Boxes]
            for box in boxes_to_delete:
                box.FBDelete()

        else:
            print(f"Constraint relation with name '{relation_name}' not found.")

    def createChainScale(self, Clist, YList, ZList, scale_relations):
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

        distance = calculate_distance_between_models(Clist[0], Clist[1])
        # print(distance)
        Relation = scale_relations
        """
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
        """
        for idx, (child, Y, Z) in enumerate(zip(Clist, YList, ZList)):
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

            # 创建加法函数并计算距离的和
            Add_Distances = Relation.CreateFunctionBox("Number", "Add (a + b)")
            Add_Distances_A = Find_AnimationNode(Add_Distances.AnimationNodeInGet(), 'a')
            Add_Distances_B = Find_AnimationNode(Add_Distances.AnimationNodeInGet(), 'b')
            Add_Distances_Result = Find_AnimationNode(Add_Distances.AnimationNodeOutGet(), 'Result')

            FBConnect(Distance1_result, Add_Distances_A)
            FBConnect(Distance2_result, Add_Distances_B)

            # 创建一个除法函数以将和除以2得到平均值
            Average = Relation.CreateFunctionBox("Number", "Divide (a/b)")
            Average_A = Find_AnimationNode(Average.AnimationNodeInGet(), 'a')
            Average_B = Find_AnimationNode(Average.AnimationNodeInGet(), 'b')
            Average_Result = Find_AnimationNode(Average.AnimationNodeOutGet(), 'Result')
            Average_B.WriteData([2])  # 除以2
            FBConnect(Add_Distances_Result, Average_A)

            Vector_to_Number = Relation.CreateFunctionBox('Converters', 'Number to Vector')
            Vector_to_Number_X = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'X')

            # Vector_to_Number_X.WriteData([1])
            # FBConnect(Divide_Result, Vector_to_Number_X)

            Vector_to_Number_Y = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'Y')
            Vector_to_Number_Z = Find_AnimationNode(Vector_to_Number.AnimationNodeInGet(), 'Z')
            Vector_to_Number_result = Find_AnimationNode(Vector_to_Number.AnimationNodeOutGet(), 'Result')

            FBConnect(Sender1_Translation, Distance1_v1)
            FBConnect(Sender2_Translation, Distance1_v2)

            FBConnect(Sender1_Translation, Distance2_v1)
            FBConnect(Sender3_Translation, Distance2_v2)
            FBConnect(Average_Result, Vector_to_Number_X)
            FBConnect(Average_Result, Vector_to_Number_Y)
            FBConnect(Average_Result, Vector_to_Number_Z)
            FBConnect(Vector_to_Number_result, receiver1_Scaling)

            Relation.SetBoxPosition(Sender1, 0, idx * 200)
            Relation.SetBoxPosition(receiver1, 2000, idx * 200)
            Relation.SetBoxPosition(Sender2, 0, idx * 200 + 60)
            Relation.SetBoxPosition(Sender3, 0, idx * 200 + 120)
            Relation.SetBoxPosition(Distance1, 400, idx * 200)
            Relation.SetBoxPosition(Distance2, 400, idx * 200 + 60)
            Relation.SetBoxPosition(Vector_to_Number, 1600, idx * 200)

            Relation.SetBoxPosition(Add_Distances, 800, idx * 200)
            Relation.SetBoxPosition(Average, 1200, idx * 200)

    def find_scale_relations(self):
        """
        查找场景中所有名字结尾为 '_scale_relation'（不区分大小写）的 FBConstraintRelation 对象。
        返回符合条件的长名字列表。
        """
        scale_relations = []
        for obj in FBSystem().Scene.Constraints:
            if isinstance(obj, FBConstraintRelation):
                # 将名字转换为小写来检查结尾
                if obj.LongName.lower().endswith("_scale_relation"):
                    scale_relations.append(obj.LongName)

        return scale_relations

    def find_object_by_long_name(self, long_name):
        """
        根据给定的长名字查找场景中是否存在符合条件的对象。
        如果找到则返回该对象，否则返回 None。
        """
        for obj in FBSystem().Scene.Constraints:
            if obj.LongName == long_name:
                return obj
        return None

    def main(self):
        relationlist = self.find_scale_relations()
        for name in relationlist:
            print(name)
            Y, Z, C = self.classify_null_objects_by_relation(name)


            print("Objects in Y list (ending with 'U数字_Y' or 'L数字_Y'):")
            for obj in Y:
                print(obj.LongName)

            print("\nObjects in Z list (ending with 'U数字_Z' or 'L数字_Z'):")
            for obj in Z:
                print(obj.LongName)

            print("\nObjects in C list (ending with '_FKcon_offset' and without 'rig'):")
            for obj in C:
                print(obj.LongName)

            if not Y or not Z or not C:
                continue
            scale_relations = self.find_object_by_long_name(name)

            # 将 relation 的 Active 属性设置为 False
            if scale_relations:
                scale_relations.Active = False

            scale_relations = FBConstraintRelation(name + "_fix")

            self.createChainScale(C, Y, Z, scale_relations)

            # 操作完成后将 Active 设置为 True
            if scale_relations:
                scale_relations.Active = True


main = Fix_tool()
main.main()