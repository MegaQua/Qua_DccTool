from pyfbsdk import *

def process_offset_objects(search_keyword, action_keyword=None):
    def Transformation_lock(targetlist, attr="all"):
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

    # 获取当前的场景
    scene = FBSystem().Scene
    # 存储找到的对象
    offset_objects = []

    # 遍历场景中的所有对象
    for obj in scene.Components:
        # 跳过FBVideoIn和FBVideoOut对象
        if isinstance(obj, (FBVideoIn, FBVideoOut, FBAudioOut, FBAudioIn)):
            continue
        if obj.Name.endswith(search_keyword):
            offset_objects.append(obj)

    # 如果找到了对象，进行相应操作
    if offset_objects:
        for obj in offset_objects:
            obj.Selected = True  # 选择对象
        if action_keyword is None:
            for obj in offset_objects:
                print("Found and selected object:", obj.Name)
        elif action_keyword == "Lock":
            Transformation_lock(offset_objects)
        else:
            print(f"Unknown action keyword: {action_keyword}")
    else:
        print("No objects found with the specified search keyword.")

# 调用函数，搜索以 '_jointCon' 结尾的对象，并根据操作关键字进行操作
search_keyword = '_curveCon'

process_offset_objects(search_keyword)