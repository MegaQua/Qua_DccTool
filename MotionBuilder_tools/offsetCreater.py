from pyfbsdk import FBSystem, FBModelNull, FBMatrix, FBGetSelectedModels, FBModelList


def create_offset_for_selected():
    # 获取当前选中的对象列表
    selected_objects = FBModelList()
    FBGetSelectedModels(selected_objects)

    # 遍历选中的对象
    for obj in selected_objects:
        # 获取父对象并临时断开父子关系
        parent = obj.Parent
        if parent:
            obj.Parent = None  # Temporarily detach from parent

            # 根据当前对象的名称和约定，修改名字
            new_name = insert_before_last_digit(obj.Name, "offset")

            # 创建一个新的空对象作为偏移，传递新名称
            offset = FBModelNull(new_name)

            # 获取原对象的全局变换矩阵
            matrix = FBMatrix()
            obj.GetMatrix(matrix)

            # 应用这个矩阵到偏移对象
            offset.SetMatrix(matrix)

            # 重新建立新的父子关系
            offset.Parent = parent
            obj.Parent = offset

            print(f"Created offset '{offset.Name}' between {parent.Name} and {obj.Name}.")
        else:
            print(f"No parent found for {obj.Name}, no offset created.")


def insert_before_last_digit(name, text):
    import re
    # 在名字的最后一个数字前插入指定的文本
    match = re.search(r'\d+$', name)
    if match:
        position = match.start()
        return name[:position] + text + name[position:]
    else:
        return name + text


create_offset_for_selected()
