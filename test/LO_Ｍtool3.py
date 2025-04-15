import maya.cmds as cmds

# 定义目标材质球名称和纹理文件路径
materials_to_check = {
    "itm0037_0211_mtrl": r"K:\LO\01_Send_Data\to_Cygames\202502xx_data\Maya\model\sourceimages\itm0037_tentacle01_col.tga",
    "itm0037_0212_mtrl": r"K:\LO\01_Send_Data\to_Cygames\202502xx_data\Maya\model\sourceimages\itm0037_tentacle02_col.tga",
    "itm0037_011_mtrl": r"K:\LO\01_Send_Data\to_Cygames\202502xx_data\Maya\model\sourceimages\itm0037_tentacle01_col.tga",
    "itm0037_011_tentacle_mtrl": r"K:\LO\01_Send_Data\to_Cygames\202502xx_data\Maya\model\sourceimages\itm0037_tentacle01_col.tga",
}
materials_to_check2 = {
    "itm0037_0211_mtrl": "itm0037_021_01_mtrl",
    "itm0037_0212_mtrl": "itm0037_021_02_mtrl",
    "itm0037_011_mtrl": "itm0037_011_mtrl",
    "itm0037_011_tentacle_mtrl": "itm0037_011_mtrl",
}


# 新建 lambert 材质球并设置属性
def create_lambert_material(material_name, texture_file):
    try:
        # 创建 Lambert 材质
        lambert_material = cmds.shadingNode("lambert", asShader=True, name=material_name)
        print(f"创建了新的 Lambert 材质: {lambert_material}")

        # 设置材质属性
        #cmds.setAttr(f"{lambert_material}.diffuse", 0.8)
        #cmds.setAttr(f"{lambert_material}.ambientColor", 0.2, 0.2, 0.2, type="double3")

        # 创建文件纹理节点
        file_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name="file1")
        cmds.setAttr(f"{file_node}.fileTextureName", texture_file, type="string")

        # 连接文件纹理到 Color 属性
        cmds.connectAttr(f"{file_node}.outColor", f"{lambert_material}.color", force=True)

        print(f"纹理文件已链接到 {lambert_material}.color，路径为: {texture_file}")
        return lambert_material
    except Exception as e:
        print(f"创建 Lambert 材质失败: {e}")
        return None


# 遍历材质绑定的对象并重新绑定到新材质
def reassign_material(original_material, new_material):
    try:
        shading_groups = cmds.listConnections(original_material, type="shadingEngine")
        if shading_groups:
            for sg in shading_groups:
                objects = cmds.sets(sg, query=True)
                if objects:
                    for obj in objects:
                        cmds.select(obj, replace=True)
                        cmds.hyperShade(assign=new_material)
                        print(f"对象 {obj} 已重新绑定到材质 {new_material}")
    except Exception as e:
        print(f"重新绑定材质失败: {e}")


# 主逻辑
for old_material_name, texture_file_path in materials_to_check.items():
    new_material_name = materials_to_check2.get(old_material_name, old_material_name)

    if cmds.objExists(old_material_name):
        material_types = ["lambert", "blinn", "phong", "aiStandardSurface"]
        if cmds.nodeType(old_material_name) in material_types:
            try:
                renamed_material = f"{old_material_name}_old"
                cmds.rename(old_material_name, renamed_material)
                print(f"材质球 '{old_material_name}' 已重命名为 '{renamed_material}'。")
            except Exception as e:
                print(f"重命名失败: {e}")
        else:
            print(f"'{old_material_name}' 存在，但它不是有效的材质类型。")
    else:
        print(f"材质球 '{old_material_name}' 不存在。")

    # 创建新的 Lambert 材质
    new_lambert_material = create_lambert_material(new_material_name, texture_file_path)

    # 遍历场景中的所有材质
    all_materials = cmds.ls(materials=True)
    for mat in all_materials:
        if old_material_name in mat and mat != old_material_name:
            print(f"发现相关材质球: {mat}")
            reassign_material(mat, new_lambert_material)
