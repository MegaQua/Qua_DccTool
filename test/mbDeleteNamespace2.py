from pyfbsdk import *
from PySide2 import QtWidgets, QtCore

class NamespaceTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Namespace Manager")
        self.setGeometry(100, 100, 500, 350)

        # Layout
        layout = QtWidgets.QVBoxLayout()

        # 选择旧 Namespace 下拉菜单
        self.old_ns_label = QtWidgets.QLabel("Select Namespace to Modify:")
        self.old_ns_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.old_ns_label)
        layout.addWidget(self.old_ns_dropdown)

        # 选择新 Namespace 下拉菜单
        self.new_ns_label = QtWidgets.QLabel("Select New Namespace:")
        self.new_ns_dropdown = QtWidgets.QComboBox()
        layout.addWidget(self.new_ns_label)
        layout.addWidget(self.new_ns_dropdown)

        # 按钮
        self.find_button = QtWidgets.QPushButton("Find and Print Objects")
        self.rename_button = QtWidgets.QPushButton("Find and Rename Namespace")
        self.delete_button = QtWidgets.QPushButton("Delete Namespace")

        # 绑定按钮事件
        self.find_button.clicked.connect(self.find_namespace_objects)
        self.rename_button.clicked.connect(self.rename_namespace)
        self.delete_button.clicked.connect(self.delete_namespace)

        # 添加按钮到布局
        layout.addWidget(self.find_button)
        layout.addWidget(self.rename_button)
        layout.addWidget(self.delete_button)

        # **日志窗口**
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)  # 只读模式
        layout.addWidget(self.log_box)

        self.setLayout(layout)

        # 初始填充 Namespace 列表
        self.refresh_namespaces()

    def log_message(self, message):
        """在日志窗口追加文本"""
        self.log_box.append(message)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())  # 自动滚动

    def refresh_namespaces(self):
        """获取场景中的所有 Namespace 并更新下拉菜单"""
        scene = FBSystem().Scene
        namespaces = set()

        for obj in scene.Components:
            try:
                obj_name = obj.LongName
                if obj_name and ":" in obj_name:
                    namespace = obj_name.split(":")[0]
                    namespaces.add(namespace)
            except Exception:
                continue  # 遇到异常对象跳过

        self.old_ns_dropdown.clear()
        self.new_ns_dropdown.clear()

        if namespaces:
            sorted_ns = sorted(namespaces)
            self.old_ns_dropdown.addItems(sorted_ns)
            self.new_ns_dropdown.addItems(sorted_ns)
        else:
            self.old_ns_dropdown.addItem("No Namespace Found")
            self.new_ns_dropdown.addItem("No Namespace Found")

    def get_namespace_objects(self, namespace):
        """查找指定命名空间的对象，跳过无法解析的对象和 FBVideoIn, FBVideoOut, FBAudioIn, FBAudioOut"""
        scene = FBSystem().Scene
        namespace_objects = []

        ignored_types = {"FBVideoIn", "FBVideoOut", "FBAudioIn", "FBAudioOut", "FBTake"}

        for obj in scene.Components:
            try:
                obj_type = obj.ClassName()  # 先获取类型
                if obj_type in ignored_types:
                    continue  # 跳过四种类型的对象

                obj_name = obj.LongName  # 之后再尝试获取名字
                if obj_name and obj_name.startswith(namespace + ":"):
                    namespace_objects.append(obj)
            except Exception as e:
                self.log_message(f"⚠ Skipped an object due to error: {e}")

        return namespace_objects

    def find_namespace_objects(self):
        """查找并打印指定 Namespace 下的所有对象"""
        old_namespace = self.old_ns_dropdown.currentText().strip()
        if not old_namespace or old_namespace == "No Namespace Found":
            self.log_message("⚠ No valid namespace selected.")
            return

        namespace_objects = self.get_namespace_objects(old_namespace)

        if namespace_objects:
            self.log_message(f"✅ Found {len(namespace_objects)} objects in namespace '{old_namespace}':")
            for obj in namespace_objects:
                self.log_message(f" - {obj.LongName} ({obj.ClassName()})")
        else:
            self.log_message(f"❌ No objects found in namespace '{old_namespace}'.")

    def rename_namespace(self):
        """查找 Namespace 下所有对象并改名"""
        old_namespace = self.old_ns_dropdown.currentText().strip()
        new_namespace = self.new_ns_dropdown.currentText().strip()

        if not old_namespace or old_namespace == "No Namespace Found":
            self.log_message("⚠ No valid namespace selected.")
            return
        if not new_namespace or new_namespace == old_namespace:
            self.log_message("⚠ Please select a different new namespace.")
            return

        namespace_objects = self.get_namespace_objects(old_namespace)

        if namespace_objects:
            self.log_message(f"🔄 Renaming {len(namespace_objects)} objects from '{old_namespace}' to '{new_namespace}':")

            for obj in namespace_objects:
                try:
                    old_name = obj.LongName
                    new_name = new_namespace + old_name[len(old_namespace):]  # 替换 namespace
                    obj.LongName = new_name  # 修改对象名称
                    self.log_message(f"✔ Renamed: {old_name} → {new_name}")
                except Exception as e:
                    self.log_message(f"❌ Failed to rename {obj}: {e}")

            self.log_message(f"✅ Namespace '{old_namespace}' successfully renamed to '{new_namespace}'.")
            self.refresh_namespaces()  # 更新 Namespace 列表
        else:
            self.log_message(f"❌ No objects found in namespace '{old_namespace}'.")

    def delete_namespace(self):
        """删除指定的 Namespace"""
        old_namespace = self.old_ns_dropdown.currentText().strip()
        if not old_namespace or old_namespace == "No Namespace Found":
            self.log_message("⚠ No valid namespace selected.")
            return

        try:
            FBSystem().Scene.NamespaceDelete(old_namespace)
            self.log_message(f"🗑 Namespace '{old_namespace}' and all its objects have been deleted.")
            self.refresh_namespaces()  # 更新 Namespace 列表
        except Exception as e:
            self.log_message(f"❌ Failed to delete namespace '{old_namespace}': {e}")

# 创建并显示 UI
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])
window = NamespaceTool()
window.show()
