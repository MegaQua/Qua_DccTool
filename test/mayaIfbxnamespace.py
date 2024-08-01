# -*- coding: utf-8 -*-
import maya.cmds as mc
import maya.mel as mel


def FBXImportToTargetNamespace(file_path, namespace_list):
    currentNs = mc.namespaceInfo(cur=True)

    for ns in namespace_list:
        # Set namespace
        if not mc.namespace(ex=':%s' % ns):
            mc.namespace(add=':%s' % ns)
        mc.namespace(set=':%s' % ns)

        # Import FBX
        mel.eval('FBXImport -f "%s"' % file_path)

        # Return to current namespace
        mc.namespace(set=currentNs)


# 文件路径
file_path = "D:/export/_fbx/test.fbx"

# 命名空间列表
namespace_list = [
    "enm0065_001_00", "enm0065_001_01", "enm0065_001_02", "enm0065_001_03", "enm0065_001_04",
    "enm0065_001_05", "enm0065_001_06", "enm0065_001_07", "enm0065_001_08",
    "enm0065_001_09", "enm0065_001_10", "enm0065_001_11", "enm0065_001_12",
    "enm0065_001_13", "enm0065_001_14", "enm0065_001_15", "enm0065_001_16",
    "enm0065_001_17", "enm0065_001_18", "enm0065_001_19", "enm0065_001_20",
    "enm0065_001_21", "enm0065_001_22", "enm0065_001_23"
]

# 调用函数
FBXImportToTargetNamespace(file_path, namespace_list)
