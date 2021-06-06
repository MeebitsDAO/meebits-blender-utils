blender MeebitRig.blend --background --python meebit_export_to_fbx.py -- --meebit c:\meebits\14544\meebit_14544_t.vox
blender MeebitRig.blend --background --python meebit_export_to_vrm.py -- --meebit c:\meebits\14544\meebit_14544_t.vox


Generate batch conversion script for several meebits in directory on windows
forfiles /p E:\meebits\meebitsdao /m *_t.vox /c "cmd /c echo blender MeebitRig.blend --background --python meebit_export_to_vrm.py -- --meebit @PATH" > run_convert.bat