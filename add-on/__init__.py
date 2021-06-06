bl_info = {
    "name": "Meebit (.vox)",
    "author": "Dagfinn Parnas based on technistguru/MagicaVoxel_Importer",
    "version": (0, 9, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import Meebit from .vox file",
    "warning": "",
    "wiki_url": "",
    "support": 'TESTING',
    "category": "Import-Export"}


if "bpy" in locals():
    import importlib
    if "meebit_core" in locals():
        importlib.reload(meebit_core)


# Responsibility
# - Defines a python package
# - Registers the ImportMeebit via register()
# - ImportMeebit defines the user interface of the import and the user exposed options
# - ImportMeebit.execute() triggers the import through meebit_core.import



import os

import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, CollectionProperty, EnumProperty
from bpy.types import Operator

import struct

"""
This imports Meebits VOX files to Blender.

It uses code from the following repo under gpl 3.0 license.
https://github.com/technistguru/MagicaVoxel_Importer

Vox file format:
https://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox.txt
https://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox-extension.txt

Usage:
Import add-on via Edit-Preferences
Run from "File->Import" menu and then select meebit .vox file
"""
class ImportMeebit(Operator, ImportHelper):
    bl_idname = "import_meebit.vox"
    bl_label = "Import meebit"
    bl_options = {'PRESET', 'UNDO'}
    
    files: CollectionProperty(name="File Path",
                              description="File path used for importing the meebit .vox file",
                              type=bpy.types.OperatorFileListElement) 

    directory: StringProperty()
    
    filename_ext = ".vox"
    filter_glob: StringProperty(
        default="*.vox",
        options={'HIDDEN'},
    )



    optimize_import_for_type: EnumProperty(name = "",
                                description = "Optimize Meebit import based on usage",
                                items = (
                                    ('Blender', 'Blender scene rendering', "Optimize for blender scene rendering"),
                                    ('VRM', 'VRM export (beta)', "Optimize for 3D avatar for VR in VRM format"),
                                ),
                                default = 'Blender')

    join_meebit_armature: BoolProperty(name = "Rig with Meebit armature",
                            description = "Rig if there exist an armature with name 'MeebitArmature'",
                            default = True)

    scale_meebit_armature: BoolProperty(name = "Scale Meebit armature to fit",
                            description = "Scale armature dimension to fit meebit dimensions",
                            default = True)                            

    shade_smooth_meebit: BoolProperty(name = "Shade smooth",
                            description = "Shade smooth set for meebit",
                            default = True)

    mtoon_shader: BoolProperty(name = "Set shader 'MToon_unversioned'",
                            description = "Automatically set a shader which can be used for VRM format",
                            default = True)                               

    override_materials: BoolProperty(name = "Override materials if they exist", default = False)                            

    # Not used directly
    voxel_size: FloatProperty(name = "Voxel Size",
                                description = "Side length, in blender units, of each voxel.",
                                default=0.025)

    # Not used directly
    material_type: EnumProperty(name = "",
                                description = "How color and material data is imported",
                                items = (
                                    ('None', 'None', "Don't import palette."),
                                    ('SepMat', 'Separate Materials', "Create a material for each palette color."),
                                    ('VertCol', 'Vertex Colors', "Create one material and store color and material data in vertex colors."),
                                    ('Tex', 'Textures', "Generates textures to store color and material data.")
                                ),
                                default = 'SepMat')

    # Not used directly
    gamma_correct: BoolProperty(name = "Gamma Correct Colors",
                                description = "Changes the gamma of colors to look closer to how they look in MagicaVoxel. Only applies if Palette Import Method is Seperate Materials.",
                                default = True)
    
    # Not used directly
    gamma_value: FloatProperty(name = "Gamma Correction Value",
                                default=2.2, min=0)
    

    
    #Not used directly
    cleanup_mesh: BoolProperty(name = "Cleanup Mesh",
                                description = "Merge overlapping verticies and recalculate normals.",
                                default = True)
    
    #Not used
    create_lights: BoolProperty(name = "Add Point Lights",
                                description = "Add point lights at emissive voxels for Eevee.",
                                default = False)
    
    #Not used directly
    create_volume: BoolProperty(name = "Generate Volumes",
                                description = "Create volume objects for volumetric voxels.",
                                default = False)
    #Not used directly
    organize: BoolProperty(name = "Organize Objects",
                            description = "Organize objects into collections.",
                            default = True)
    

    def execute(self, context):
        from . import meebit_core

        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)
        
        # Must be in object mode
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            print("Failed to set object mode. Continuing")
            pass
        

        for path in paths:
            meebit_core.import_meebit_vox(path, self)
        
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Meebits add-on for blender", icon='HEART')
        row= box.row()
        row.label(text = "Brought to you by @MeebitsDAO")

        # layout.prop(self, "voxel_size")
        
        box = layout.box()
        box.label(text="Optimize import for", icon='ARMATURE_DATA')    

        import_type = box.column(align=True)
        import_type.prop(self, "optimize_import_for_type")
        
        # if self.material_type == 'SepMat':
        #    layout.prop(self, "gamma_correct")
        #    if self.gamma_correct:
        #        layout.prop(self, "gamma_value")

        
        # layout.prop(self, "cleanup_mesh")
        # layout.prop(self, "create_lights")
        # layout.prop(self, "organize")

        box = layout.box()
        box.label(text="Advanced options", icon='MODIFIER_OFF')    
        secondary_options = box.column(align=True)

        if self.optimize_import_for_type == 'VRM': 
            secondary_options.prop(self, "mtoon_shader")

        secondary_options.prop(self, "join_meebit_armature")
        if self.join_meebit_armature:
            secondary_options.prop(self, "scale_meebit_armature")
        
        secondary_options.prop(self, "shade_smooth_meebit")
        #layout.prop(self, "create_volume")
        
        secondary_options.prop(self, "override_materials")


def menu_func_import(self, context):
    self.layout.operator(ImportMeebit.bl_idname, text="Meebit (.vox)")

def register():
    bpy.utils.register_class(ImportMeebit)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportMeebit)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()        