"""
This script meebits to a blender scene 

It uses code from the following repo under gpl 3.0 license.
https://github.com/technistguru/MagicaVoxel_Importer

Usage:
blender MeebitRig.blend --background --python meebit_export_to_fbx.py -- --meebit E:\meebits\14544\meebit_14544_t.vox
"""

# Debug tips. Shift+F4 for python console .  obj = bpy.data.objects['meebit_16734_t'] to get object

import os
import sys
import argparse
import code
from pathlib import Path

import bpy

import struct
# Debug python loading modules
# print(sys.path)
# print(sys.executable)

# Add data path where the scene was loaded to 
blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)


# Dev tips - Trigger interactive console 
#code.interact(local=locals())

from meebit_core import import_meebit_vox


# Argument parser from https://blender.stackexchange.com/a/6844
class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())

class MeebitImportOption(object):
    pass



parser = ArgumentParserForBlender()


#parser.add_argument("-q", "--quack",
#                    action="store_true",
#                    help="Quacks bar times if activated.")

parser.add_argument("-m", "--meebit",
                    action="store",
                    help="Meebit .vox file in t-pose",
                    required=True)

args = parser.parse_args()
meebitPath = args.meebit

print("Meebit import to scene script")
print(meebitPath)

options=MeebitImportOption()
options.voxel_size=.025
options.optimize_import_for_type='Blender'
#options.material_type='Tex'
options.mtoon_shader= True
options.shade_smooth_meebit= True
options.gamma_correct= True
options.gamma_value= 2.2
options.override_materials = False
options.cleanup_mesh=True
options.create_lights=False
options.join_meebit_armature=True
options.scale_meebit_armature= True
options.organize=True
options.create_volume=False

import_meebit_vox(meebitPath,options)

# Attempt to export all objects
objects = bpy.context.scene.objects

bpy.ops.object.select_all(action='SELECT')
exportFilename = Path(meebitPath).stem + '.fbx'
bpy.ops.export_scene.fbx(filepath=exportFilename, use_selection=True)