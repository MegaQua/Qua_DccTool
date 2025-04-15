from pyfbsdk import *
from PySide2 import QtWidgets, QtGui, QtCore
import re


# 执行
# 函数 名称指定
class Fix_tool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MB_jointPath_tool")
        self.setGeometry(300, 300, 400, 200)

        self.selected_items = []
        self.namespace_types = {
            "enm0065": "type_enm",
            "itm0035": "type_itm35",
            "itm0036": "type_itm36",
            "itm0037": "type_itm37",
            "itm0038": "type_itm38",
            "itm0039": "type_itm39"
        }
    def open_selection_dialog(self):
        # 模拟 relationlist 数据
        relationlist = ["item1", "item2", "item3", "item4"]

        # 创建一个选择窗口
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Items")
        dialog_layout = QtWidgets.QVBoxLayout(dialog)

        # 创建一个用于存储选择项的字典
        self.item_checkboxes = {}

        # 为 relationlist 中的每个项目创建一个复选框
        for item in relationlist:
            checkbox = QtWidgets.QCheckBox(item)
            dialog_layout.addWidget(checkbox)
            self.item_checkboxes[item] = checkbox

        # 添加确认按钮
        ok_button = QtWidgets.QPushButton("OK")
        dialog_layout.addWidget(ok_button)
        ok_button.clicked.connect(lambda: self.get_selected_items(dialog))



    def get_selected_items(self, dialog):
        # 收集选中的项目
        selected_items = [item for item, checkbox in self.item_checkboxes.items() if checkbox.isChecked()]
        print("Selected items:", selected_items)

        # 执行处理
        for name in selected_items:
            print(f"Processing {name}")
            # 此处可以插入 main 函数中针对选项的处理逻辑

        dialog.close()

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

        # 根据不同的命名空间设置匹配模式
        if "enm0065" in namespace:
            y_pattern = re.compile(f"^{namespace}.*?_main_offset_Y$", re.IGNORECASE)
            z_pattern = re.compile(f"^{namespace}.*?_main_offset_Z$", re.IGNORECASE)
            fkcon_offset_pattern = re.compile(f"^{namespace}.*?_main_offset$", re.IGNORECASE)

        elif "itm0035" in namespace:
            # 新的 Y、Z 和 C 列表匹配模式
            y_pattern = re.compile(f"^{namespace}:tentacle[0-9]+_main_offset_Y$", re.IGNORECASE)
            z_pattern = re.compile(f"^{namespace}:tentacle[0-9]+_main_offset_Z$", re.IGNORECASE)
            fkcon_offset_pattern = re.compile(f"^{namespace}:tentacle[0-9]+_main_offset$", re.IGNORECASE)

        elif "itm0037" in namespace:
            # 根据 relation_long_name 中是否包含 U 或 L 设置前缀
            if "U_scale_Relation" in relation_long_name:
                prefix = "U"
            elif "L_scale_Relation" in relation_long_name:
                prefix = "L"
            else:
                prefix = ""

            if prefix:  # 仅在有前缀时匹配 Y 和 Z
                y_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_Y)$", re.IGNORECASE)
                z_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_Z)$", re.IGNORECASE)
                fkcon_offset_pattern = re.compile(f"^{namespace}:(?!.*rig)(?!.*Cuvre).*(?:{prefix}[0-9]+_FKcon_offset)$", re.IGNORECASE)
            else:
                y_pattern = z_pattern = fkcon_offset_pattern = None  # 无效匹配模式

        elif "itm0036" in namespace:
            # 匹配 tentacleCenter[1-2位数字]_Y, tentacleCenter[1-2位数字]_Z 和 tentacleCenter[1-2位数字]_FKcon_offset
            y_pattern = re.compile(f"^{namespace}:tentacleCenter[0-9]{{1,2}}_Y$", re.IGNORECASE)
            z_pattern = re.compile(f"^{namespace}:tentacleCenter[0-9]{{1,2}}_Z$", re.IGNORECASE)
            fkcon_offset_pattern = re.compile(f"^{namespace}:tentacleCenter[0-9]{{1,2}}_FKcon_offset$", re.IGNORECASE)



        else:
            # 不存在其他情况，直接跳过
            y_pattern = z_pattern = fkcon_offset_pattern = None

        # 遍历场景中的所有 FBModelNull 对象
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelNull):
                obj_name = obj.LongName

                # 根据名字匹配条件，将对象添加到相应列表
                if y_pattern and y_pattern.match(obj_name):
                    y_objects.append(obj)
                elif z_pattern and z_pattern.match(obj_name):
                    z_objects.append(obj)
                elif fkcon_offset_pattern and fkcon_offset_pattern.match(obj_name):
                    fkcon_offset_objects.append(obj)

        # 检查列表是否为空，如果为空则打印 relation_long_name
        if not y_objects or not z_objects or not fkcon_offset_objects:
            empty_lists = []
            if not y_objects:
                empty_lists.append("'Y' list")
            if not z_objects:
                empty_lists.append("'Z' list")
            if not fkcon_offset_objects:
                empty_lists.append("'FKCon Offset' list")
            print(f"No matches found in {', '.join(empty_lists)} for '{relation_long_name}'.")

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

    def find_relations_in_namespace(self, namespace):
        """
        查找场景中属于指定命名空间并符合条件的 FBConstraintRelation 对象。

        参数:
        namespace (str): 要匹配的命名空间。

        返回:
        list: 符合条件的关系对象名称列表。
        """
        relations = []
        for obj in FBSystem().Scene.Constraints:
            if isinstance(obj, FBConstraintRelation):
                # 检查对象的命名空间是否符合指定的namespace并且名字以指定格式结尾
                if obj.LongName.startswith(f"{namespace}:") and obj.LongName.lower().endswith("_scale_relation"):
                    relations.append(obj.LongName)

        return relations

    def find_object_by_long_name(self, long_name):
        """
        根据给定的长名字查找场景中是否存在符合条件的对象。
        如果找到则返回该对象，否则返回 None。
        """
        for obj in FBSystem().Scene.Constraints:
            if obj.LongName == long_name:
                return obj
        return None

    def show_selection_dialog(self, relationlist):
        # 创建一个选择窗口
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Items to Process")
        dialog_layout = QtWidgets.QVBoxLayout(dialog)

        # 创建复选框存储字典
        self.item_checkboxes = {}

        # 为每个 relation 创建一个复选框，默认勾选
        for item in relationlist:
            checkbox = QtWidgets.QCheckBox(item)
            checkbox.setChecked(True)
            dialog_layout.addWidget(checkbox)
            self.item_checkboxes[item] = checkbox

        # 添加OK按钮
        ok_button = QtWidgets.QPushButton("OK")
        dialog_layout.addWidget(ok_button)
        ok_button.clicked.connect(dialog.accept)  # 点击OK关闭对话框

        result = dialog.exec_()  # 显示对话框并等待用户操作

        # 如果用户点击OK以外的操作，直接退出
        if result != QtWidgets.QDialog.Accepted:
            self.selected_items = []
            return False

        # 保存选中的项
        self.selected_items = [item for item, checkbox in self.item_checkboxes.items() if checkbox.isChecked()]
        return True
    def show_completion_message(self):
        # 创建完成提示对话框，使用日语表示“完了しました”
        QtWidgets.QMessageBox.information(self, "完了", "操作が完了しました。")

    def find_namespaces(self):
        """
        遍历场景中的所有对象，根据命名空间判断类型，并将符合条件的命名空间存储到一个列表中。
        返回包含有效命名空间的列表。
        """
        found_namespaces = []

        # 遍历场景中的所有对象
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelNull):  # 仅检查FBModelNull对象
                namespace = obj.LongName.split(":")[0] if ":" in obj.LongName else ""

                # 检查命名空间是否包含字典中的任意一个键
                if any(ns_type in namespace for ns_type in self.namespace_types.keys()):
                    if namespace not in found_namespaces:
                        found_namespaces.append(namespace)

        return found_namespaces

    def remove_joint_fcurve_in_namespace(self, namespace):
        """
        在指定的命名空间中找到所有 joint 对象并删除其 fcurve 动画。

        参数:
        namespace (str): 要操作的命名空间。
        """
        print(f"Removing fcurve animations for joints in namespace: {namespace}")
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{namespace}:"):
                #print(obj.LongName)

                for prop in obj.PropertyList:
                    if hasattr(prop, 'IsAnimated') and prop.IsAnimated():
                        anim_node = prop.GetAnimationNode()
                        if anim_node and anim_node.FCurve:
                            fcurve = anim_node.FCurve
                            key_count = fcurve.KeyGetCount()
                            for i in range(key_count - 1, -1, -1):  # 从最后一个键开始删除
                                fcurve.KeyRemove(i)
                            #print(f"All keyframes removed for joint: {obj.LongName}")

    def set_inherit_type_for_namespace(self, namespace):
        """
        在指定的命名空间中找到所有 joint 对象，并将其 InheritType 属性值设置为 1。

        参数:
        namespace (str): 要操作的命名空间。
        """
        #print(f"Setting InheritType to 1 for joints in namespace: {namespace}")
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{namespace}:"):
                # 遍历 joint 的属性列表
                for prop in obj.PropertyList:
                    if prop.Name == "InheritType":
                        try:
                            prop.Data = 1  # 将 InheritType 属性值设置为 1
                            #print(f"Set InheritType of {obj.LongName} to 1.")
                        except Exception as e:
                            print(f"Failed to set InheritType for {obj.LongName}: {e}")
                        break  # 找到 InheritType 属性后即可退出属性循环

    def plot_keyframes_for_namespace_joints(self, namespace):
        """
        对符合指定命名空间且名字不是 'Root' 的所有 joint 对象执行关键帧 Plot 操作，
        并根据提供的设置参数进行配置。

        参数:
        namespace (str): 要操作的命名空间。
        """
        print(f"Plotting keyframes for joints in namespace: {namespace} (excluding 'Root')")

        # 设置 Plot 选项
        plot_options = FBPlotOptions()
        plot_options.PlotOnFrame = True  # 勾选 "Plot On Frame"
        plot_options.PlotAllTakes = False  # 不勾选 "Plot All Takes"
        plot_options.PlotRate = FBTime(0, 0, 0, 1, 0, FBTimeMode.kFBTimeMode60Frames)  # 设置帧率为 60 FPS

        # Filters To Apply
        plot_options.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll  # 设置 Rotation Filter 为 "Unroll"
        plot_options.UseConstantKeyReducer = True  # 勾选 "Constant Key Reducer"
        plot_options.ConstantKeyReducerKeepOneKey = True  # 勾选 "Keep at least one keyframe"

        # Smart Plot 选项
        plot_options.PlotPrecisionMode = True  # 勾选 "Smart Plot"
        plot_options.PlotPrecisionModeIncreaseFidelity = True  # 勾选 "Increase Fidelity"
        plot_options.PlotFidelityTolerance = 0.25  # 设置 Fidelity Keys Tolerance 为 0.25

        # 其他选项
        plot_options.PlotExtensions = True  # 勾选 "Plot Extensions"
        plot_options.PlotLockedProperties = True  # 勾选 "Plot Locked Properties"
        plot_options.PlotAuxEffectors = False  # 不勾选 "Plot Aux Effectors"
        plot_options.PlotDeformation = True  # 勾选 "Evaluate Deformation"

        # 遍历场景中的所有对象并选择符合条件的 joints
        joints_to_plot = []
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{namespace}:") and "Root" not in obj.LongName:
                print(f"Adding joint to plot list: {obj.LongName}")
                joints_to_plot.append(obj)

        # 设置选中的对象为要 Plot 的 joint
        for joint in joints_to_plot:
            joint.Selected = True

        # 执行 Plot 操作
        FBSystem().CurrentTake.PlotTakeOnSelected(plot_options)

        # 清除选择
        for joint in joints_to_plot:
            joint.Selected = False

        print("Plotting completed for specified joints.")

    def main(self):
        # 取消场景中所有对象的选择
        for obj in FBSystem().Scene.Components:
            obj.Selected = False

        namespaces = self.find_namespaces()
        self.show_selection_dialog(namespaces)
        namespaces = self.selected_items
        print(namespaces)
        for namespace in namespaces:
            relationlist = self.find_relations_in_namespace(namespace)
            print(relationlist)
            self.remove_joint_fcurve_in_namespace(namespace)
            self.set_inherit_type_for_namespace(namespace)
            for relation in relationlist:
                Y, Z, C = self.classify_null_objects_by_relation(relation)
                if not Y or not Z or not C:
                    continue
                scale_relations = self.find_object_by_long_name(relation)

                # 将 relation 的 Active 属性设置为 False
                if scale_relations:
                    scale_relations.Active = False

                scale_relations = FBConstraintRelation(relation + "_fix")

                self.createChainScale(C, Y, Z, scale_relations)

                # 操作完成后将 Active 设置为 True
                if scale_relations:
                    scale_relations.Active = True
            #self.plot_keyframes_for_namespace_joints(namespace)
            # 最后一步：选择需要处理的 joints
            for obj in FBSystem().Scene.Components:
                if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{namespace}:") and "Root" not in obj.LongName:
                    obj.Selected = True  # 选择符合条件的 joint
        """
        #print(relationlist)
        self.show_selection_dialog(relationlist)

        selected_items = self.selected_items

        for name in selected_items:

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
        """

        self.show_completion_message()

main = Fix_tool()
main.main()