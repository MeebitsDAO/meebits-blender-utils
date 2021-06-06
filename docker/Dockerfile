# Blender docker file from https://hub.docker.com/r/nytimes/blender https://github.com/nytimes/rd-blender-docker

FROM nytimes/blender:latest

# Copy scripts
# Copy blender scene with aramature
# Copy VRM add-on
# All in one layer to current directory
copy code/* MeebitRig.blend code/VRM_Addon_for_Blender-release.zip ./

# Install VRM add-on through our script
run blender -b  -y  --python blender_install_vrm_addon.py