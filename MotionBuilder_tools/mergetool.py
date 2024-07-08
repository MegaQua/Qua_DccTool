from pyfbsdk import *

def merge_files(file_list):
    for file_path, count in file_list:
        for _ in range(count):
            merge_options = FBFbxOptions(True)
            # Turn off Merge File window
            merge_options.ShowOptionsDialog = False
            # Merge all Elements. Merge All Animation
            merge_options.SetAll(FBElementAction.kFBElementActionAppend, True)
            merge_options.Materials = FBElementAction.kFBElementActionMerge
            merge_options.Textures = FBElementAction.kFBElementActionMerge
            merge_options.Video = FBElementAction.kFBElementActionMerge
            ## --------------------------- Open File ---------------------------
            # Merge File without modifying take names
            FBApplication().FileMerge(file_path, False, merge_options)

# Example usage:
file_list = [
    [r"K:\LO\06_Animations\01_MotionBuilder\01_Assets\02_Props\tentacle\_old\LO_tentacle_v004_fix.fbx", 10],
    [r"K:\LO\06_Animations\01_MotionBuilder\01_Assets\02_Props\tentacle\_old\LO_tentacle_foot_v001_fix.fbx", 8],
    [r"K:\LO\06_Animations\01_MotionBuilder\01_Assets\02_Props\tentacle\_old\LO_tentacle_roll_v001_fix.fbx", 0],
    [r"K:\LO\06_Animations\01_MotionBuilder\01_Assets\02_Props\tentacle\_old\LO_tentacle_horizontalCut_v001_fix.fbx", 0],
    [r"K:\LO\06_Animations\01_MotionBuilder\01_Assets\02_Props\tentacle\_old\LO_tentacle_VerticalCut_v002_fix.fbx", 0],
]
merge_files(file_list)
