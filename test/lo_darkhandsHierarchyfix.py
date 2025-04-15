from pyfbsdk import *

def create_hidden_null(name, target_obj):
    """
    创建一个 Null 对象，并将其位置设置为 target_obj 的位置，同时隐藏它。

    :param name: 新 Null 的名称 (str)
    :param target_obj: 参考对象 (FBModel) - Null 将被放置在该对象的位置
    :return: 新创建的 Null (FBModelNull)
    """
    if not isinstance(target_obj, FBModel):
        #print(f"Error: {target_obj} 不是 FBModel 类型，无法创建 {name}")
        return None

    # 创建 Null
    null_obj = FBModelNull(name)

    # 复制位置
    pos = FBVector3d()
    target_obj.GetVector(pos, FBModelTransformationType.kModelTranslation)
    null_obj.SetVector(pos, FBModelTransformationType.kModelTranslation)

    # 隐藏 Null
    null_obj.Show = False

    # 添加到场景
    null_obj.Parent = target_obj.Parent  # 保持相同的父级
    null_obj.Selected = False  # 确保不被选中

    #print(f"Created hidden null: {null_obj.LongName} at position {pos}")
    return null_obj

def getModelByName(LongName):
    """
    根据 LongName 查找场景中的模型（包括 FBModel 和 FBModelNull）
    """
    for obj in FBSystem().Scene.Components:  # 遍历所有组件
        if isinstance(obj, (FBModel, FBModelNull)):  # 兼容 FBModel 和 FBModelNull
            if obj.LongName == LongName:
                return obj
    return None  # 未找到返回 None

def deselect_all():
    """
    取消所有选中对象
    """
    for obj in FBSystem().Scene.Components:  # 遍历所有对象
        if isinstance(obj, FBModel):  # 只操作模型对象
            obj.Selected = False

def fix_hierarchy():
    """
    查找符合条件的 namespace，并获取 grp_body，同时存储需要选中的 grp_body
    """
    scene = FBSystem().Scene
    namespaces = set()
    grp_body_list = []  # 存储符合条件的 grp_body 对象

    # 遍历所有对象，找到符合条件的 namespace 并存储 grp_body
    for model in scene.Components:
        if isinstance(model, FBModel):  # 处理所有模型对象
            if ":" in model.LongName:  # 确保有 namespace
                name_space = model.LongName.split(':')[0]  # 提取 namespace
                if name_space.startswith("itm000"):
                    namespaces.add(name_space)
                if model.Name == r"Wrist_R Parent/Child":
                    model.Name = "Wrist_R"

    # 对 namespace 排序后进行处理
    namespaces_list = sorted(namespaces)

    for ns in namespaces_list:
        grp_body = getModelByName(f"{ns}:grp_body")
        body = getModelByName(f"{ns}:body")

        if not body:
            print(f"Warning: {ns}:body not found, skipping...")
            continue  # 跳过这个 namespace

        body.Name = "msh_body"

        if grp_body:
            # 记录符合条件的 grp_body
            grp_body_list.append(grp_body)

            # 确保 `grp_body` 存在后再创建 null
            grp_msh_body = create_hidden_null(f"{ns}:grp_msh_body", grp_body)
            grp_main = create_hidden_null(f"{ns}:grp_main", grp_body)

            if grp_msh_body and grp_main:
                grp_msh_body.Parent = grp_body  # 修正 Parent 赋值方法
                grp_main.Parent = grp_msh_body
                body.Parent = grp_main
                print(f"process finish on {ns}")
            else:
                print(f"Error: Failed to create grp_msh_body or grp_main for {ns}")

    # 清空所有选中对象
    deselect_all()

    # 选中存储的 grp_body
    for grp in grp_body_list:
        grp.Selected = True

# 运行函数
fix_hierarchy()
