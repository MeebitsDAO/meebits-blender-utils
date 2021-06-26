"""
This script meebits to a blender scene 

It uses code from the following repo under gpl 3.0 license.
https://github.com/technistguru/MagicaVoxel_Importer

Usage:
blender MeebitRig.blend --background --python meebit_export_to_vrm.py -- --meebit E:\meebits\14544\meebit_14544_t.vox
"""

# Debug tips. Shift+F4 for python console .  obj = bpy.data.objects['meebit_16734_t'] to get object

import os
import sys
import argparse
import code
from pathlib import Path

import requests
import re

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
options.optimize_import_for_type='VRM'
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


# Before exporting, let's set the VRM meta information ref 
# https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0_draft/meta.md
# https://vrm.dev/en/docs/univrm/meta/univrm_meta/
fileNameNoEnding = (Path(meebitPath).stem)

# Expected value of fileNameNoEnding  = 'meebit_19666_t_solid'
meebitId = re.search('meebit_([^_]*)',fileNameNoEnding).group(1)
# Remove leading zeros
meebitId = meebitId.lstrip('0')
print(f'Meebit id from filename is {meebitId}')

try:
    # Do screenscraping from ll site for owner wallet
    print(f'Making HTTP request to https://meebits.larvalabs.com/meebits/detail?index={meebitId}')
    response = requests.get(f'https://meebits.larvalabs.com/meebits/detail?index={meebitId}')
    ownerWallet = re.search('account.address=([^"]*)',response.text).group(1)

    # Set these values in blender for the VRM export add-on to include them
    meebitArmature = bpy.data.objects['MeebitArmature']
    meebitArmature['version'] = '0.9.3'  # matches the meebit blender add-on version
    meebitArmature['author'] = ownerWallet # wallet id for the owner when the VRM was created
    meebitArmature['contactInformation'] = f'https://meebits.larvalabs.com/meebits/detail?index={meebitId}' # To be update to metaverse sign-up info
    meebitArmature['reference'] = 'https://meebitsdao.world/' # meebits dao promotion
    meebitArmature['title'] = f'Meebit #{meebitId}' # meebit number reference
    meebitArmature['otherPermissionUrl'] = f'https://meebits.larvalabs.com/meebits/detail?index={meebitId}'  # meebit url
    meebitArmature['otherLicenseUrl'] = 'https://meebits.larvalabs.com/meebits/termsandconditions' # meebits terms and conditions
    # Leave default value of these for now
    # meebitArmature['allowedUserName': 'OnlyAuthor']
    # meebitArmature['violentUssageName': 'Disallow']
    # meebitArmature['sexualUssageName': 'Disallow']
    # meebitArmature['commercialUssageName': 'Disallow']
    # meebitArmature['licenseName': 'Redistribution_Prohibited']
except Exception as e:
    print("Failed to set VRM metadata")
    print(e)

exportFilename = fileNameNoEnding+ '.vrm'
bpy.ops.export_scene.vrm('EXEC_DEFAULT', filepath=exportFilename)
print("Meebit VRM successfully written to " + exportFilename)

try:
    #Get photo as well
    print(f'Making HTTP request to https://meebits.larvalabs.com/meebitimages/characterimage?index={meebitId}&type=full')
    response = requests.get(f'https://meebits.larvalabs.com/meebitimages/characterimage?index={meebitId}&type=full')
    with open(fileNameNoEnding+ '.jpg',"wb") as file:
        file.write(response.content)
except Exception as e:
    print("Failed to set VRM metadata")
    print(e)

print("Don't forget to follow @MeebitsDAO")