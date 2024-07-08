from pyfbsdk import *

def Find_AnimationNode( pParent, pName ):
    # Boxが指定された名前のノードを持っているかを調べる。
    lResult = None
    for lNode in pParent.Nodes:
        if lNode.Name == pName:
            lResult = lNode
            break
    return lResult
def getConstraintsByName(constraintsName):
    lConstraints = FBSystem().Scene.Constraints  # 获取当前场景中的所有约束列表
    for each in lConstraints:  # 遍历场景中的所有约束
        if each.Name == constraintsName:  # 检查约束名称是否匹配
            return each  # 如果找到匹配的约束，立即返回它

    # 如果遍历完成后没有找到匹配的约束，则创建一个新的约束
    return FBConstraintRelation(constraintsName)  # 创建一个新的约束并返回


# 使用函数检查或创建名为"Relation test"的约束
result = getConstraintsByName("Relation test")

print(result)
lMgr = FBConstraintManager()
Path = lMgr.TypeCreateConstraint("Path")
lRecever = result.ConstrainObject(Path)