import maya.cmds as cmds
import random
import string
import re

def rename_objects_with_prefix(prefix):
    """
    遍历场景中的物体，找到以指定前缀开头，且名称完全等于前缀或剩余部分不包含下划线的物体，
    按照逻辑直接完成所有重命名。

    Args:
        prefix (str): 指定的前缀字符。
    """
    # 找到符合条件的物体，获取短名称、完整路径，并判断是否为子对象
    objects = [
        {
            "object": obj,
            "long_name": obj,
            "short_name": obj.split('|')[-1],
            "is_child": '|' in obj and len(obj.split('|')) > 2
        } for obj in cmds.ls(transforms=True, long=True)
        if obj.split('|')[-1].startswith(prefix)
        and (obj.split('|')[-1] == prefix or "_" not in obj.split('|')[-1][len(prefix):])
        and "GP_ALL" not in obj  # 跳过长名字中包含 GP_ALL 的对象
    ]

    if not objects:
        #print(f"没有找到以'{prefix}'开头且后续部分不含下划线的物体。")
        return

    # 按序直接对每个物体执行所有重命名
    for i, obj_data in enumerate(objects):
        obj = obj_data["object"]
        long_name = obj_data["long_name"]
        is_child = obj_data["is_child"]

        # 生成随机名称（第一步）
        random_number = ''.join(random.choices(string.digits, k=8))
        temp_name = f"{prefix}{random_number}"
        try:
            # 第一步：重命名为随机名称
            cmds.rename(long_name, temp_name)
            # 动态更新长名称
            new_long_name = long_name.rsplit('|', 1)[0] + '|' + temp_name if '|' in long_name else temp_name

            # 第二步：生成最终名称
            if is_child:
                parent_name = new_long_name.rsplit('|', 1)[0].split('|')[-1]  # 获取父对象名称
                suffix = parent_name[-1] if parent_name else 'A'  # 使用父名称的最后一个字符作为后缀
                final_name = f"{prefix}{suffix}"
            else:
                final_name = f"{prefix}{chr(65 + i)}"  # chr(65) 为 'A'

            # 第二步：重命名为最终名称
            print(i,f"重命名'{obj}'为'{final_name}'")
            cmds.rename(new_long_name, final_name)

        except RuntimeError as e:
            pass
            #print(f"无法重命名对象 {long_name}: {e}")

    #print(f"已完成以'{prefix}'开头的物体的全部重命名操作。")


def rename_objects_by_dict(rename_dict):
    """
    Rename objects in the Maya scene based on a provided dictionary.

    Args:
        rename_dict (dict): A dictionary where keys are the prefixes to look for and
                            values are the new names to rename matching objects to.
    """
    for prefix, new_name in rename_dict.items():
        # Find all objects in the scene, including DAG hierarchy
        all_objects = cmds.ls(dag=True, long=True)

        for obj in all_objects:
            # Check if the object's name starts with the prefix
            if obj.split('|')[-1].startswith(prefix):
                try:
                    # Generate a unique new name to avoid conflicts
                    unique_name = cmds.rename(obj, new_name)
                    #print(f"Renamed {obj} to {unique_name}")
                except RuntimeError as e:
                    print(f"Error renaming {obj}: {e}")

rename_dict = {
    "itm0037_011_1_bend": "itm0037_022_1_",
    "itm0037_011_2_bend": "itm0037_022_2_",
    "itm0037_011_high_bend_GP": "itm0037_022_",
    "itm0037_011_1_high_twist": "itm0037_023_1_",
    "itm0037_011_2_high_twist": "itm0037_023_2_",
    "itm0037_011_high_twist": "itm0037_023_",
    "itm0037_011_1_high": "itm0037_021_1_",
    "itm0037_011_2_high": "itm0037_021_2_",
    "itm0037_011_high": "itm0037_021_",
    "itm0037_011_1_low_bend": "itm0037_025_1_",
    "itm0037_011_2_low_bend": "itm0037_025_2_",
    "itm0037_011_low_bend": "itm0037_025_",
    "itm0037_011_1_low_twist": "itm0037_026_1_",
    "itm0037_011_2_low_twist": "itm0037_026_2_",
    "itm0037_011_low_twist": "itm0037_026_",
    "itm0037_011_1_low": "itm0037_024_1_",
    "itm0037_011_2_low": "itm0037_024_2_",
    "itm0037_011_low": "itm0037_024_",
    "itm0037_011_B": "itm0037_011_",
    "itm0037_011_C": "itm0037_012_",
    "itm0037_011_D_bend": "itm0037_013_",
    "itm0037_011_D_straight": "itm0037_014_",
    "itm0037_011_D_twist": "itm0037_015_",
}
P = {
    "itm0037_011_high_bend_GP": "itm0037_022_",
    "itm0037_011_high_twist": "itm0037_023_",
    "itm0037_011_high": "itm0037_021_",
    "itm0037_011_low_bend": "itm0037_025_",
    "itm0037_011_low_twist": "itm0037_026_",
    "itm0037_011_low": "itm0037_024_",
    "itm0037_011_B": "itm0037_011_",
    "itm0037_011_C": "itm0037_012_",
    "itm0037_011_D_bend": "itm0037_013_",
    "itm0037_011_D_straight": "itm0037_014_",
    "itm0037_011_D_twist": "itm0037_015_",
}
C = {
    "itm0037_011_1_bend": "itm0037_022_1_",
    "itm0037_011_2_bend": "itm0037_022_2_",
    "itm0037_011_1_high_twist": "itm0037_023_1_",
    "itm0037_011_2_high_twist": "itm0037_023_2_",
    "itm0037_011_1_high": "itm0037_021_1_",
    "itm0037_011_2_high": "itm0037_021_2_",
    "itm0037_011_1_low_bend": "itm0037_025_1_",
    "itm0037_011_2_low_bend": "itm0037_025_2_",
    "itm0037_011_1_low_twist": "itm0037_026_1_",
    "itm0037_011_2_low_twist": "itm0037_026_2_",
    "itm0037_011_1_low": "itm0037_024_1_",
    "itm0037_011_2_low": "itm0037_024_2_",
}
def delete_object_keep_children(search_string):
    # 查找名称中包含特定字符串的对象
    objects = cmds.ls(f"*{search_string}*")
    if not objects:
        print(f"没有找到名称中包含 '{search_string}' 的对象。")
        return

    for obj in objects:
        # 获取对象的子节点
        children = cmds.listRelatives(obj, children=True, fullPath=True)
        if children:
            # 将子节点的父级设为世界（顶层）
            for child in children:
                cmds.parent(child, world=True)
        # 删除对象
        cmds.delete(obj)
        print(f"删除了对象 '{obj}'，并将其子节点移至顶层。")


delete_object_keep_children("itm0037_011_distant")

rename_objects_by_dict(rename_dict)

for key, value in P.items():
    #print(value)
    rename_objects_with_prefix(value)
for key, value in C.items():
    #print(value)
    rename_objects_with_prefix(value)