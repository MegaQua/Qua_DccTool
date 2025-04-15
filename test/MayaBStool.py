import maya.cmds as cmds

# 指定 blendShape 节点
blendShape_node = 'blendShape1'

# 尝试获取 inputTarget[0].inputTargetGroup[0].inputGeomTarget 的连接对象
connection_0 = cmds.listConnections(f'{blendShape_node}.inputTarget[0].inputTargetGroup[0].inputGeomTarget', destination=False, source=True,
                                    plugs=True)

if connection_0:
    # 打印连接对象
    print(f"Connection at inputTargetGroup[0]: {connection_0[0]}")

    # 断开现有连接
    cmds.disconnectAttr(connection_0[0], f'{blendShape_node}.inputTarget[0].inputTargetGroup[0].inputGeomTarget')
    print(f"Disconnected connection at inputTargetGroup[0].")
else:
    print(f"No connection found at inputTarget[0].inputTargetGroup[0].inputGeomTarget.")
