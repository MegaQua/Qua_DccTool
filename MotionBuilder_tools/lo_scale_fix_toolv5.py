from pyfbsdk import *


def find_constraints_in_namespace(self, namespace):
    """
    在指定命名空间中查找三类符合条件的约束对象：
    1. 名称中带有 "scale" 的 FBConstraintRelation（不区分大小写）。
    2. 类型为 Parent/Child Constraint 的约束。
    3. 类型为 Scale Constraint 的约束。

    参数:
    namespace (str): 要匹配的命名空间。

    返回:
    list: 符合条件的约束对象名称列表。
    """
    constraints = []
    for obj in FBSystem().Scene.Constraints:
        # 条件 1: 如果是 FBConstraintRelation 并且名称中包含 "scale"
        if isinstance(obj, FBConstraintRelation) and obj.LongName.startswith(f"{namespace}:"):
            if "scale" in obj.LongName.lower():
                constraints.append(obj.LongName)

        # 条件 2: 类型为 Parent/Child Constraint
        elif isinstance(obj, FBConstraintParentChild) and obj.LongName.startswith(f"{namespace}:"):
            constraints.append(obj.LongName)

        # 条件 3: 类型为 Scale Constraint
        elif isinstance(obj, FBConstraintScale) and obj.LongName.startswith(f"{namespace}:"):
            constraints.append(obj.LongName)

    return constraints
