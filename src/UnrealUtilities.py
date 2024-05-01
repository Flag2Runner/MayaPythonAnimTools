import unreal
import os

def ImportSkeltalMesh(meshPath):
    importTask = CreateBaseImportTask(meshPath)
    
    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = True
    importOptions.import_materials = True
    #this imports blendshapes
    importOptions.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
    #this tells unreal to use frame 0 as the default pose
    importOptions.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', True)

    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])
    return importTask.get_objects()[0]


def CreateBaseImportTask(meshPath)-> unreal.AssetImportTask:
    importTask = unreal.AssetImportTask()
    importTask.filename = meshPath

    fileName = os.path.basename(meshPath).split('.')[0]
    importTask.destination_path = '/Game/_MyFiles/Characters/' + fileName
    importTask.automated = True
    importTask.save = True
    importTask.replace_existing = True
    return importTask

def ImportAnimation(mesh : unreal.SkeletalMesh, animPath):
    importTask = CreateBaseImportTask(animPath)
    meshDir = os.path.dirname(mesh.get_path_name())
    importTask.destination_path = meshDir + "/animations"
    
    importOptions = unreal.FbxImportUI()
    importOptions.import_mesh = False
    importOptions.import_animations = True
    importOptions.import_as_skeletal = True
    importOptions.skeleton = mesh.skeleton

    importOptions.set_editor_property('automated_import_should_detect_type', False)
    importOptions.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    importOptions.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)
    
    importTask.options = importOptions

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([importTask])

def ImportMeshAndAnimation(meshPath, animDir):
    mesh = ImportSkeltalMesh(meshPath)
    for fileName in os.listdir(animDir):
        if ".fbx" in fileName:
            animPath = os.path.join(animDir, fileName)
            ImportAnimation(mesh, animPath)

#ImportMeshAndAnimation("D:/Profile Redirect/leesqui1/Desktop/out/alex.fbx", "D:/Profile Redirect/leesqui1/Desktop/out/anim" )



