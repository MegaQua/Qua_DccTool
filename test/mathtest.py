from pyfbsdk import *
def Find_AnimationNode( pParent, pName ):
    # Boxが指定された名前のノードを持っているかを調べる。
    lResult = None
    for lNode in pParent.Nodes:
        if lNode.Name == pName:
            lResult = lNode
            break
    return lResult
testRelation = FBConstraintRelation("test_Relation")
constraint_manager = FBConstraintManager()

path1 = constraint_manager.TypeCreateConstraint("Path")
path2 = constraint_manager.TypeCreateConstraint("Path")
warp_out=Find_AnimationNode( path1.AnimationNodeInGet(), 'Warp' )
warp_in=Find_AnimationNode( path2.AnimationNodeInGet(), 'Warp' )

a=testRelation.SetAsSource(path1)
b=testRelation.ConstrainObject(path2)
testdivide=testRelation.CreateFunctionBox("Number", "Divide (a/b)")
a  = Find_AnimationNode( testdivide.AnimationNodeInGet(), 'a' )
b  = Find_AnimationNode( testdivide.AnimationNodeInGet(), 'b' )
dout  = Find_AnimationNode( testdivide.AnimationNodeInGet(), 'Result' )
c = testdivide.AnimationNodeInGet()
for i in c.Nodes:
    print (i.Name)
#print(a,b,dout)
b.WriteData([10.0])
FBConnect( dout , warp_in )