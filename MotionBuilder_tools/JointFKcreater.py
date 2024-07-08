from pyfbsdk import FBSystem, FBModelMarker, FBModelNull, FBConstraintManager, FBMatrix, FBGetSelectedModels, FBModelList


def create_controller_and_constraints():
    selected_joints = FBModelList()
    FBGetSelectedModels(selected_joints)

    # 用于存储joint和其对应控制器的字典
    joint_to_controller = {}

    # 第一遍，为每个joint创建控制器和偏移对象
    for joint in selected_joints:
        controller_name = insert_before_last_digit(joint.Name, "Con")
        controller = FBModelMarker(controller_name)

        # 获取原对象的全局变换矩阵并应用
        matrix = FBMatrix()
        joint.GetMatrix(matrix)
        controller.SetMatrix(matrix)

        # 创建控制器的偏移对象
        offset_name = insert_before_last_digit(controller.Name, "offset")
        offset = FBModelNull(offset_name)
        offset.SetMatrix(matrix)

        # 保存控制器信息以便后续查找
        joint_to_controller[joint] = (controller, offset)

    # 第二遍，设置每个控制器的父对象和偏移对象的父对象
    for joint, (controller, offset) in joint_to_controller.items():
        if joint.Parent and joint.Parent in joint_to_controller:
            # 将控制器的偏移对象的父对象设置为父joint的控制器
            offset.Parent = joint_to_controller[joint.Parent][0]  # Parent joint's controller
        else:
            offset.Parent = None  # 顶级joint或找不到父控制器

        # 设置控制器的父对象为其偏移对象
        controller.Parent = offset

        # 创建父子约束，使joint跟随控制器
        constraint = FBConstraintManager().TypeCreateConstraint("Parent/Child")
        constraint.ReferenceAdd(1, controller)  # Controller is the parent
        constraint.ReferenceAdd(0, joint)  # Joint is the child
        constraint.Name = f"Parent {controller.Name} Child {joint.Name}"  # Naming the constraint
        constraint.Active = True

        scaling_constraint = FBConstraintManager().TypeCreateConstraint("Scale")
        scaling_constraint.ReferenceAdd(1, controller)  # Controller is the source
        scaling_constraint.ReferenceAdd(0, joint)  # Joint is the target
        scaling_constraint.Name = f"Scaling {controller.Name} Controls {joint.Name}"  # Naming the constraint
        scaling_constraint.Active = True
        print(
            f"Controller '{controller.Name}' with offset '{offset.Name}' created for joint '{joint.Name}', and constraint established with name '{constraint.Name}'.")


def insert_before_last_digit(name, text):
    import re
    # 在名字的最后一个数字前插入指定的文本
    match = re.search(r'\d+$', name)
    if match:
        position = match.start()
        return name[:position] + text + name[position:]
    else:
        return name + text


create_controller_and_constraints()
