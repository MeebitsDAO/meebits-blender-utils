import os
import bpy

bpy.ops.preferences.addon_install (overwrite=True, target='DEFAULT', filepath=os.getcwd() + 'VRM_Addon_for_Blender-release.zip')
bpy.ops.preferences.addon_enable(module = 'VRM_Addon_for_Blender-release')
bpy.ops.wm.save_userpref()