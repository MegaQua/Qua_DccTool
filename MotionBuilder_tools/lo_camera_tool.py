from pyfbsdk import *
from pyfbsdk_additions import *
from PySide2 import QtCore, QtWidgets, QtGui
import time

class CameraTransferTool(QtWidgets.QWidget):
    def __init__(self):
        super(CameraTransferTool, self).__init__()

        self.setWindowTitle("Camera Transfer Tool")

        self.vcam_list = []
        self.rigcam_list = []

        self.populate_cameras()
        layout = QtWidgets.QGridLayout(self)

        # 第一行
        vcam_label = QtWidgets.QLabel("Vcam List")
        self.vcam_combo = QtWidgets.QComboBox()
        for vcam in self.vcam_list:
            self.vcam_combo.addItem(vcam)
        layout.addWidget(vcam_label, 0, 0)
        layout.addWidget(self.vcam_combo, 0, 1, 1, 3)

        # 第二行
        rigcam_label = QtWidgets.QLabel("Rig Cam List")
        self.rigcam_combo = QtWidgets.QComboBox()
        for rigcam in self.rigcam_list:
            self.rigcam_combo.addItem(rigcam)
        layout.addWidget(rigcam_label, 1, 0)
        layout.addWidget(self.rigcam_combo, 1, 1, 1, 3)

        # 第三行
        self.transfer_button = QtWidgets.QPushButton("Transfer Animation")
        layout.addWidget(self.transfer_button, 2, 1, 1, 2)

        # 连接按钮到相应的函数
        self.transfer_button.clicked.connect(self.transfer_animation)

        self.setLayout(layout)
        self.show()

    def populate_cameras(self):
        # 遍历所有模型，寻找以vcam_开头的camera对象
        for model in FBSystem().Scene.Components:
            try:
                model_name = model.Name
            except:
                continue
            if isinstance(model, FBCamera):
                if model.Name.startswith("vcam_"):
                    self.vcam_list.append(model.LongName)
            elif isinstance(model, FBModel):
                if "Cam_Rig" in model.Name.encode('utf-8').decode('utf-8'):
                    self.rigcam_list.append(model.LongName)



    def transfer_animation(self):
        def process_frames():
            system = FBSystem()
            current_time = system.LocalTime

            # 获取当前帧
            current_frame = current_time.GetFrame()


            # 移动到下一帧
            next_time = current_time
            next_time.SetFrame(current_frame + 1)
            system.CurrentTake.LocalTime = next_time
            next_frame = next_time.GetFrame()


            # 移动到上一帧
            previous_time = next_time
            previous_time.SetFrame(next_frame - 1)
            system.CurrentTake.LocalTime = previous_time
            previous_frame = previous_time.GetFrame()

        def Align(pModel, pAlignTo, pAlignTransX, pAlignTransY, pAlignTransZ, pAlignRotX, pAlignRotY, pAlignRotZ):
            lAlignTransPos = FBVector3d()
            lModelTransPos = FBVector3d()
            lAlignRotPos = FBVector3d()
            lModelRotPos = FBVector3d()

            pAlignTo.GetVector(lAlignTransPos)
            pModel.GetVector(lModelTransPos)

            pAlignTo.GetVector(lAlignRotPos, FBModelTransformationType.kModelRotation)
            pModel.GetVector(lModelRotPos, FBModelTransformationType.kModelRotation)

            if pAlignTransX:
                lModelTransPos[0] = lAlignTransPos[0]
            if pAlignTransY:
                lModelTransPos[1] = lAlignTransPos[1]
            if pAlignTransZ:
                lModelTransPos[2] = lAlignTransPos[2]

            if pAlignRotX:
                lModelRotPos[0] = lAlignRotPos[0]
            if pAlignRotY:
                lModelRotPos[1] = lAlignRotPos[1]
            if pAlignRotZ:
                lModelRotPos[2] = lAlignRotPos[2]

            pModel.SetVector(lModelTransPos)
            pModel.SetVector(lModelRotPos, FBModelTransformationType.kModelRotation)
        def set_current_keyframe(model):
            current_time = FBSystem().LocalTime
            translation_prop = model.PropertyList.Find('Lcl Translation')
            rotation_prop = model.PropertyList.Find('Lcl Rotation')

            model.Translation.GetAnimationNode().KeyAdd(current_time, list(translation_prop))
            model.Rotation.GetAnimationNode().KeyAdd(current_time, list(rotation_prop))

        # 获取选中的vcam和rigcam
        vcam_name = self.vcam_combo.currentText()
        rigcam_namespace = self.rigcam_combo.currentText().split(':')[0]

        # 获取对象
        vcam = FBFindModelByLabelName(vcam_name)
        cam_move = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Move")
        Cam_Interest = FBFindModelByLabelName(f"{rigcam_namespace}:Cam_Interest")

        aim_null = FBModelNull(f"{vcam_name}_aim")
        aim_null.Parent = vcam
        aim_null.Translation = FBVector3d(0, 0, 0)
        aim_null.Rotation = FBVector3d(0, 0, 0)
        aim_null.Scaling = FBVector3d(1, 1, 1)

        if not vcam or not cam_move or not Cam_Interest:
            FBMessageBox("Error", "Selected cameras or rig not found!", "OK")
            return
        """"""
        # 获取vcam的帧范围
        translation_x_node = vcam.PropertyList.Find('Lcl Translation').GetAnimationNode().Nodes[0]
        fcurve = translation_x_node.FCurve
        key_times = set(key.Time for key in fcurve.Keys)
        start_time = min(key_times)
        end_time = max(key_times)

        start_frame = start_time.GetFrame()
        end_frame = end_time.GetFrame()

        # 遍历帧范围
        for frame in range(start_frame, end_frame + 1):
            time = FBTime(0, 0, 0, frame)
            FBPlayerControl().Goto(time)
            process_frames()

            # 处理Translation
            vcam_prop = vcam.PropertyList.Find('Lcl Translation')
            cam_move_prop = cam_move.PropertyList.Find('Lcl Translation')
            if vcam_prop and cam_move_prop:
                for i in range(3):  # X, Y, Z
                    value = vcam_prop.GetAnimationNode().Nodes[i].FCurve.Evaluate(time)
                    cam_move_prop.SetAnimated(True)
                    cam_move_prop.GetAnimationNode().Nodes[i].FCurve.KeyAdd(time, value)

            # 获取FocusDistance值并设置aim_null和Cam_Interest
            FocusDistance = vcam.PropertyList.Find('FocusDistance')
            focus_distance_value = FocusDistance.Data
            aim_null.Translation.SetAnimated(True)
            aim_null.Translation.GetAnimationNode().Nodes[0].FCurve.KeyAdd(time, focus_distance_value)
            process_frames()
            Align(Cam_Interest, aim_null, True, True, True, True, True, True)
            process_frames()
            set_current_keyframe(Cam_Interest)

# 显示工具窗口
LO_camera = CameraTransferTool()
