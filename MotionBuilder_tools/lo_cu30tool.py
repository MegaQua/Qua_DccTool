import re

class c30tool():
    def select_path_constraints(self):
        """
        清空当前选择，并在场景中找到符合以下命名模式的 constraint 对象并选择它们：
        1. 以 'Main_Path' 结尾。
        2. 以 'Finger_Path' 结尾并跟随一个大写字母。
        """
        print("Clearing selection and selecting constraints with names ending in 'Main_Path' or 'Finger_Path' followed by a capital letter")

        # 清空当前选择
        FBSystem().Scene.Evaluate()  # 确保场景更新
        for obj in FBSystem().Scene.Components:
            obj.Selected = False

        # 定义正则模式
        pattern = re.compile(r"(Main_Path$|Finger_Path[A-Z]$)")

        # 遍历并选择符合模式的 constraint 对象
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBConstraint) and pattern.search(obj.LongName):
                obj.Selected = True
                print(f"Constraint selected: {obj.LongName}")
tool=c30tool()
tool.select_path_constraints