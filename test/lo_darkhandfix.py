from pyfbsdk import *


def rename_wrist_r():
    scene = FBSystem().Scene

    for model in scene.Components:
        if isinstance(model, FBModelSkeleton):  # 仅处理 Joint
            # 获取短名称（去掉命名空间）
            short_name = model.Name.split(':')[-1]

            if short_name == r"Wrist_R Parent/Child":
                namespace = ':'.join(model.Name.split(':')[:-1])  # 提取命名空间
                new_name = f"{namespace}:Wrist_R" if namespace else "Wrist_R"
                model.Name = new_name
                print(f"Renamed: {model.Name}")


rename_wrist_r()
