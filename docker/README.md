# Docker for meebits blender utils
Provides access to convert meebits without installing blender locally

Steps: 
1. Install docker desktop https://docs.docker.com/get-docker/
1. Create directories containing the meebits to convert and the resulting vrm files C:\meebit_vrm_conversion\input_meebits and C:\meebit_vrm_conversion\output_vrm
(feel free to change to different folder, but then the docker run command must be updated as well)
1. Configure docker desktop to give access to files under C:\meebit_vrm_conversion\
![image](https://user-images.githubusercontent.com/1133607/120553598-f5ea2280-c3f8-11eb-9505-dc7a080fb048.png)

1. Copy your meebits meebit_xxx_t_solid.vox to meebits-blender-utils/docker/meebits
1. Open command prompt and navigate to directory meebits-blender-utils/docker
1.  Build docker image with `docker build -t blender-meebits-v1 .`
1.  Run the docker image interactively `docker run -v C:\meebit_vrm_conversion\input_meebits:/meebits -v C:\meebit_vrm_conversion\output_vrm:/output_vrm  -it blender-meebits-v1`
PS make sure the -v volume commands has full paths and not just a relative path
1.  In the container console, run `./convert_all_meebits.sh"` . Converted .vrm file will end up in the /output_vrm folder mapped to C:\meebit_vrm_conversion\output_vrm
1.  Exit container console


## Useful commands
Useful commands for docker:
- `docker images` - Get existing images
- `docker ps` - View running images
- `docker cp meebit_17871_t_solid.vox 8b7b72e384aa:/meebits` - Copy local file to docker container (8b7b72e384aa is container id found in `docker ps`)
- `docker system prune -a` - Reclaim space
