from PySide2 import QtWidgets, QtCore
from pyfbsdk import *

# 対象のネームスペースを設定
target_namespaces = {
    "itm0035_061_id0020",
    "itm0035_061_id0030",
    "itm0035_061_id0040",
    "itm0035_061_id0050",
    "itm0035_061_id0060",
    #"itm0036_011_id0010"
}


class Tool(QtWidgets.QWidget):
    def __init__(self):
        super(Tool, self).__init__()

        self.setWindowTitle("ツール - ボーン操作")
        self.resize(420, 360)

        layout = QtWidgets.QVBoxLayout(self)

        # ボタンエリア
        button_layout = QtWidgets.QGridLayout()

        self.btn_select_joints = QtWidgets.QPushButton("ボーンを選択（ネームスペース全体）")
        self.btn_unparent_bones = QtWidgets.QPushButton("Root以外のボーンをUnparent")
        self.btn_fix_inherittype = QtWidgets.QPushButton("InheritType = 1 に設定")
        self.btn_check_inherit = QtWidgets.QPushButton("InheritType ≠ 1 のボーンをチェック")

        button_layout.addWidget(self.btn_select_joints, 0, 0)
        button_layout.addWidget(self.btn_unparent_bones, 1, 0)
        button_layout.addWidget(self.btn_fix_inherittype, 2, 0)
        button_layout.addWidget(self.btn_check_inherit, 3, 0)

        layout.addLayout(button_layout)

        # ログ出力欄
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.setLayout(layout)
        self.show()

        # イベント接続
        self.btn_fix_inherittype.clicked.connect(self.fix_inherittype)
        self.btn_select_joints.clicked.connect(self.select_joint_objects)
        self.btn_unparent_bones.clicked.connect(self.unparent_bones)
        self.btn_check_inherit.clicked.connect(self.check_inherit_type)

    def log(self, text):
        self.log_box.append(text)
        print(text)

    def fix_inherittype(self):
        for ns in target_namespaces:
            count = 0
            for obj in FBSystem().Scene.Components:
                if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{ns}:"):
                    for prop in obj.PropertyList:
                        if prop.Name == "InheritType":
                            try:
                                prop.Data = 1
                                count += 1
                            except Exception as e:
                                self.log(f"[×] {obj.LongName} の InheritType を設定できませんでした: {e}")
                            break
            self.log(f"[✔] {ns} のボーン {count} 個の InheritType を 1 に設定しました")

    def select_joint_objects(self):
        """
        各ネームスペース内のすべてのボーンを選択状態にします。
        まず既存の選択をクリアしてから処理します。
        """
        # すべての選択を解除
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModel) and obj.Selected:
                obj.Selected = False

        total_selected = 0
        for ns in target_namespaces:
            count = 0
            for obj in FBSystem().Scene.Components:
                if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{ns}:"):
                    obj.Selected = True
                    count += 1
            self.log(f"[✔] {ns} のボーンを {count} 個選択しました")
            total_selected += count

        if total_selected == 0:
            self.log("[！] 対象のボーンが見つかりませんでした")


    def unparent_bones(self):
        """
        各ネームスペース内のRoot以外のボーンをUnparentします。
        """
        for ns in target_namespaces:
            count = 0
            for obj in FBSystem().Scene.Components:
                if isinstance(obj, FBModelSkeleton) and obj.LongName.startswith(f"{ns}:"):
                    short_name = obj.LongName.split(":")[-1]
                    if short_name != "Root":
                        obj.Parent = None
                        count += 1
            self.log(f"[★] {ns} のボーン（Rootを除く）{count} 個を Unparent しました")

    def check_inherit_type(self):
        failed_list = []
        for obj in FBSystem().Scene.Components:
            if isinstance(obj, FBModelSkeleton):
                for prop in obj.PropertyList:
                    if prop.Name == "InheritType" and prop.Data != 1:
                        failed_list.append(obj.LongName)
                        break
        if failed_list:
            self.log("[!] 以下のボーンは InheritType ≠ 1 です：")
            for name in failed_list:
                self.log(f"  - {name}")
        else:
            self.log("[✔] すべてのボーンの InheritType は 1 です")


# ツール起動
def show_tool():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    global tool_window
    tool_window = Tool()

show_tool()
