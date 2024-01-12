from pyfbsdk import *
from PySide2 import QtWidgets, QtGui, QtCore
import json
import os
asset_filepath ="S:\Public\qiu_yi\JCQ_Tool\data/MB_BS_Asset.json"
class MR_Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BS animation Json Importer For MB")

        layout = QtWidgets.QGridLayout(self)

        # 第一行
        target_name_label = QtWidgets.QLabel("target name")
        self.model_asset_text = QtWidgets.QLineEdit()
        self.asset_list = QtWidgets.QComboBox()
        with open(asset_filepath, "r") as f:
            json_data = json.loads(f.read())
            keys_list = list(json_data.keys())
        for i in keys_list:
            self.asset_list.addItem(i)
        layout.addWidget(target_name_label, 0, 0)
        layout.addWidget(self.model_asset_text, 0, 1,1, 3)
        layout.addWidget(self.asset_list, 0, 4)

        self.set_selection_text = QtWidgets.QLabel("or: ")
        self.set_selection_text.setAlignment(QtCore.Qt.AlignRight)
        set_selection_text_btn = QtWidgets.QPushButton("set from select")
        layout.addWidget(self.set_selection_text, 1, 3)
        layout.addWidget(set_selection_text_btn, 1, 4)
        # 第二行
        json_path_label = QtWidgets.QLabel("json file path")
        self.json_file_text = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse")
        layout.addWidget(json_path_label, 2, 0)
        layout.addWidget(self.json_file_text, 2, 1, 1, 3)
        layout.addWidget(browse_btn, 2, 4)

        # 第三行
        self.check_label = QtWidgets.QLabel("")
        self.check_image_label = QtWidgets.QLabel()
        self.check_image_label.setFixedSize(200, 200)
        pixmap = QtGui.QPixmap(r"/noimage.png")
        self.check_image_label.setPixmap(pixmap)
        check_btn = QtWidgets.QPushButton("check data")
        layout.addWidget(self.check_label, 3, 3)
        layout.addWidget(self.check_image_label, 3, 0,1,2)
        layout.addWidget(check_btn, 3, 4)

        # 第四行
        start_frame_label = QtWidgets.QLabel("import start frame")
        self.start_frame_text = QtWidgets.QLineEdit()
        end_frame_label = QtWidgets.QLabel("import end frame")
        self.end_frame_text = QtWidgets.QLineEdit()
        layout.addWidget(start_frame_label, 4, 0)
        layout.addWidget(self.start_frame_text, 4, 1)
        layout.addWidget(end_frame_label, 4, 2)
        layout.addWidget(self.end_frame_text, 4, 3)

        # 第五行

        set_frame_btn = QtWidgets.QPushButton("set import frame now")
        set_take_frame_btn = QtWidgets.QPushButton("set from take now")
        layout.addWidget(set_frame_btn, 5, 1)
        layout.addWidget(set_take_frame_btn, 5, 2)

        import_btn = QtWidgets.QPushButton("Import")
        layout.addWidget(import_btn, 6, 4)
        # 为所有按钮连接临时函数
        self.asset_list.currentIndexChanged.connect(self.list_selection_changed)
        set_selection_text_btn.clicked.connect(self.get_from_selection)
        browse_btn.clicked.connect(self.browse_path)
        check_btn.clicked.connect(self.massage_win)
        set_frame_btn.clicked.connect(self.set_start_frame_now)
        set_take_frame_btn.clicked.connect(self.set_frame_from_take)
        import_btn.clicked.connect(self.setBSkey)

        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def temp_function(self):
        sender = self.sender()
        print(f"{sender.text()} clicked")
    def set_start_frame_now(self):
        # 获取当前系统
        system = FBSystem()

        # 获取当前时间
        current_time = system.LocalTime.GetFrame()

        self.start_frame_text.setText(str(int(current_time)))

        self.end_frame_text.setText("")

    def set_frame_from_take(self):
        # 获取当前系统
        system = FBSystem()

        # 获取当前动作捕捉（Take）
        take = system.CurrentTake

        # 获取动作捕捉的起始帧和结束帧
        start_frame = take.LocalTimeSpan.GetStart().GetFrame()
        end_frame = take.LocalTimeSpan.GetStop().GetFrame()
        self.start_frame_text.setText(str(int(start_frame)))
        self.end_frame_text.setText(str(int(end_frame)))

    def get_from_selection(self):
        scene = FBSystem().Scene
        # 获取选择的物体
        selected_objects = FBModelList()
        FBGetSelectedModels(selected_objects)
        # 打印选择的物体
        selected_LS = []
        for obj in selected_objects:
            # print(obj.LongName)
            selected_LS.append(obj.LongName)
        text = ','.join(selected_LS)
        self.model_asset_text.setText(text)
    def data_check(self):

        target_text = self.model_asset_text.text()
        target_ls_str = target_text.split(",")
        target_ls = []

        scene = FBSystem().Scene
        for t in  target_ls_str:
            # 按名称查找对象
            object_found = None

            for obj in scene.Components:
                try:
                    if obj.LongName == t:
                        object_found = obj
                        #self.check_label.setText(object_found.Name)
                        target_ls.append(object_found)
                        break
                except:
                    pass
    def browse_path(self):
        path = os.getcwd()
        file_filter = "JSON Files (*.json)"
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select JSON File", path, file_filter)
        if file_path:
            self.json_file_text.setText(file_path)
        try:
            image_path = file_path.replace(".json", ".png")
            pixmap = QtGui.QPixmap(image_path)
            self.check_image_label.setPixmap(pixmap)
        except:
            pass
    def setBSkey(self):

        filepath = self.json_file_text.text()
        target_text = self.model_asset_text.text()
        target_ls_str = target_text.split(",")
        target_ls = []
        for target_name in target_ls_str:
            model = FBFindModelByLabelName(target_name)
            target_ls.append(model)
        #print (target_ls)
        start_frame = self.start_frame_text.text()
        end_frame =  self.end_frame_text.text()

        scene = FBSystem().Scene



        importjsonpath = self.json_file_text.text()
        with open(filepath, "r") as f:
            facs_data = json.loads(f.read())
            facsNames = facs_data["facsNames"]
            numPoses = facs_data["numPoses"]
            numFrames = facs_data["numFrames"]
            weightMat = facs_data["weightMat"]

        for fr in range(numFrames):
            for obj in target_ls:
                for i in range(numPoses):
                    frame = fr + int(start_frame)
                    weight = weightMat[fr][i]
                    target=obj.PropertyList.Find(str(facsNames[i]))
                    if end_frame:
                        if frame > int(end_frame):
                            break
                    if target:
                        if fr == 0 or fr + 1 == int(numFrames) or frame == end_frame:
                            target.SetAnimated(True)
                            target.GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0, frame),weight * 100)
                        else:
                            if weight!=weightMat[fr-1][i] :
                                target.GetAnimationNode().FCurve.KeyAdd(FBTime(0, 0, 0, frame), weight * 100)
        # 获取当前系统
        system = FBSystem()
        # 获取当前时间
        current_time = system.LocalTime.GetFrame()

        onetimetime = FBTime(0, 0, 0, int(current_time), 0)
        twotimetime = FBTime(0, 0, 0, int(current_time) + 1, 0)
        FBPlayerControl().Goto(twotimetime)
        FBPlayerControl().Goto(onetimetime)
        self.massage_win("Done!")
    def massage_win(self,text):
        if text == False:
            text ="text"
        message_box = QtWidgets.QMessageBox()
        message_box.setIcon(QtWidgets.QMessageBox.Warning)
        message_box.setWindowTitle("File Exists")
        message_box.setText(text)
        #message_box.addButton(QtWidgets.QMessageBox.Yes)
        #message_box.addButton(QtWidgets.QMessageBox.No)
        #message_box.setDefaultButton(QtWidgets.QMessageBox.No)
        # 设置窗口置顶
        message_box.setWindowFlags(message_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        result = message_box.exec_()
    def list_selection_changed(self, index):
        selected_asset = self.asset_list.currentText()
        with open(asset_filepath, "r") as f:
            json_data = json.loads(f.read())
        value = json_data[selected_asset]
        text = ','.join(value)
        self.model_asset_text.setText(text)
bsaj_importerMB = MR_Window()