from pyfbsdk import *
from PySide2 import QtWidgets, QtGui, QtCore
import os
import re


class PlayblastExporter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.overwriteflag = 0
        self.setWindowTitle("camera key frame Exporter for MB 0.0.2")

        layout = QtWidgets.QGridLayout(self)

        output_folder_label = QtWidgets.QLabel("Output Folder:")

        self.output_folder_text = QtWidgets.QLineEdit()
        desktop_folder = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        self.output_folder_text.setText(desktop_folder)
        output_folder_btn = QtWidgets.QPushButton("Browse Output Folder")

        filename_label = QtWidgets.QLabel("file name:")
        self.filename_text = QtWidgets.QLineEdit()
        #autoname_btn = QtWidgets.QPushButton("set camera name")

        finalname_label = QtWidgets.QLabel("final name:")
        self.finalname_label2 = QtWidgets.QLabel("")


        method_label = QtWidgets.QLabel("render with:")
        self.method_selector = QtWidgets.QComboBox(self)
        self.method_selector.addItem("keyframe on camara")
        self.method_selector.addItem("frame now")

        camera_label = QtWidgets.QLabel("camera select")
        self.camera_selector = QtWidgets.QComboBox(self)
        self.camera_selector.addItem("Camera now")
        self.add_cameras_to_selector()

        sp_label = QtWidgets.QLabel("extra ")
        self.sp_selector = QtWidgets.QComboBox(self)
        self.sp_selector.addItem("Using the parent directory as a suffix")
        self.sp_selector.addItem("None")
        self.suffix=True
        self.sp_selector.currentIndexChanged.connect(lambda index: self.set_suffix_based_on_index(index))

        Render_btn = QtWidgets.QPushButton("Render")
        # 连接按钮的信号
        output_folder_btn.clicked.connect(self.browse_output_folder)
        Render_btn.clicked.connect(self.Do_render)
        self.filename_text.textChanged.connect(lambda :self.update_final_name_label2())

        layout.addWidget(output_folder_label, 0, 0)
        layout.addWidget(self.output_folder_text, 0, 1)
        layout.addWidget(output_folder_btn, 0, 2)
        layout.addWidget(filename_label, 1, 0)
        layout.addWidget(self.filename_text, 1, 1)
        #layout.addWidget(autoname_btn, 1, 2)
        layout.addWidget(finalname_label, 2, 0)
        layout.addWidget(self.finalname_label2, 2, 1, 1, 2)
        layout.addWidget(method_label, 3, 0)
        layout.addWidget(self.method_selector, 3, 1)
        layout.addWidget(camera_label, 4, 0)
        layout.addWidget(self.camera_selector, 4, 1)
        layout.addWidget(sp_label, 5, 0)
        layout.addWidget(self.sp_selector, 5, 1)
        layout.addWidget(Render_btn, 6, 2)


        self.update_final_name_label2()
        self.resize(600, 80)  # 设置窗口的默认尺寸
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def set_suffix_based_on_index(self, index):
        if index == 0:
            self.suffix = True
        else:
            self.suffix = False
        self.update_final_name_label2()
    def update_final_name_label2(self):
        # 更新标签的文本

        filename=self.filename_text.text()
        file_format="jpg"
        pathname=self.output_folder_text.text()
        folder_name=os.path.basename(pathname)
        if self.suffix:
            file_name = pathname+"/"+str(filename)+"_"+str(folder_name)+"_####"+"."+file_format
        else:
            file_name = pathname + "/" + str(filename) +  "_####" + "." + file_format
        self.finalname_label2.setText(file_name)

    def add_cameras_to_selector(self):
        cameras = []
        for component in pyfbsdk.FBSystem().Scene.Components:
            if isinstance(component, pyfbsdk.FBCamera):
                cameras.append(component.Name)

        # 将相机添加到下拉菜单中
        for camera in cameras:
            self.camera_selector.addItem(camera)

    def get_camera_keyframes(self,camera_name):
        renderer = FBSystem().Renderer
        camera_keyframes = []

        # 获取当前活动的相机
        if renderer.GetPaneCount() > 0:
            #current_camera = renderer.GetCameraInPane(0)
            #current_camera =  camera
            scene = pyfbsdk.FBSystem().Scene
            for component in scene.Components:
                if isinstance(component, pyfbsdk.FBCamera) and component.Name == camera_name:
                    current_camera = component
                    break
            if current_camera:
                #print("Current Camera: {}".format(current_camera.Name))

                # 获取相机的动画节点
                anim_node = current_camera.Translation.GetAnimationNode()

                # 检查是否存在动画节点
                if anim_node:
                    for node in anim_node.Nodes:
                        curve = node.FCurve

                        # 检查是否存在动画曲线
                        if curve:
                            for key_index in range(len(curve.Keys)):
                                key = curve.Keys[key_index]
                                key_frame = key.Time.GetFrame()
                                camera_keyframes.append(int(key_frame))

                # 去除重复的帧号
                camera_keyframes = sorted(list(set(camera_keyframes)))

            else:
                print("No active camera found.")
        else:
            print("No active rendering pane found.")

        return camera_keyframes

    def set_current_camera(self,camera_name):
        # 获取MotionBuilder场景
        scene = pyfbsdk.FBSystem().Scene

        # 寻找具有指定名称的相机
        for component in scene.Components:
            if isinstance(component, pyfbsdk.FBCamera) and component.Name == camera_name:
                # 获取当前的视图器
                viewer = pyfbsdk.FBSystem().Renderer.GetViewerByIndex(0)
                # 设置找到的相机为活动相机
                viewer.CurrentCamera = component
                return True

        return False
    def Do_render(self):
        options=FBVideoGrabber().GetOptions()
        options.TimeSteps = FBTime(0, 0, 0, 1)
        options.CameraResolution = FBCameraResolutionMode.kFBResolutionCustom
        if not os.path.exists(os.path.dirname(self.output_folder_text.text())):
            os.makedirs(os.path.dirname(self.output_folder_text.text()))
        filename=self.filename_text.text()
        file_format="jpg"
        pathname=self.output_folder_text.text()
        folder_name=os.path.basename(pathname)
        if self.suffix:
            file_name = f"{pathname}/{str(filename)}_{str(folder_name)}_.{file_format}"
        else:
            file_name = f"{pathname}/{str(filename)}_.{file_format}"
        options.OutputFileName = file_name
        print(options.OutputFileName)
        options.TimeSpan = FBTimeSpan(FBSystem().LocalTime, FBSystem().LocalTime)


        selected_index = self.method_selector.currentIndex()
        renderwith_index =self.method_selector.currentIndex()
        if renderwith_index == 0:
            if selected_index == 0:
                camera = renderer.GetCameraInPane(0).Name
                frames = self.get_camera_keyframes(camera)
            else:
                camera=self.method_selector.currentText()
                frames = self.get_camera_keyframes(camera)
                set_current_camera(camera)
            print(f"render on {camera}")
            for frame in frames:
                if frame != 0:
                    options.TimeSpan = FBTimeSpan(FBTime(0, 0, 0, frame), FBTime(0, 0, 0, frame))
                    FBApplication().FileRender(options)
        elif renderwith_index == 1:
            current_time = pyfbsdk.FBSystem().LocalTime()
            options.TimeSpan = pyfbsdk.FBTimeSpan(pyfbsdk.FBTime(current_time), pyfbsdk.FBTime(current_time))
            FBApplication().FileRender(options)
    def browse_output_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder_path:
            self.output_folder_text.setText(folder_path)

        self.update_final_name_label2()



# 创建窗口实例
playblast_exporter = PlayblastExporter()


