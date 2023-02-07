# Video-to-svg-contour-extractions
Mere python terminal app allowing to extract contours of each frame of video and save it as svg files. These files can then be used for animation purposes for instance. Once the script is launched, the user will be able to calibrate the contour detection on the first frame of the video via 3 different parameters. These parameters correspond to the ones used in the [Canny Edge filter of opencv](https://docs.opencv.org/3.4/da/d22/tutorial_py_canny.html). Once satisfied with the results, pressing space will launch the processing of all the remaining frames of the video. The contours of each frame are saved as an svg file in dedicated saving directory. The location of this directory is specified by the user either in the command line or in the GUI version. If nothing is specified, the saving directory will be created where the python script is saved at. 
 
# Requirements
Scripts were coded on a Windows system using python 3.11.0 on a conda system. All packages that are used can be found in the `requirements.txt` file. 

# Code options
Download the `src` folder and launch the `convert-video-to-svg.py` using python. The script `convert-video-to-svg.py` allows to launch 2 versions of the app:

 - 1 using tkinter interface
 - 1 using a command line

Default launches the command line version. Comment/uncomment the code under the line `if __name__ == '__main__': ` in the script `convert-video-to-svg.py` to switch versions. 

Helper for the command line version :
```
usage: convert-video-to-svg.py [-h] [-save_path SAVE_PATH] [-ksize kernel size] file

positional arguments:
  file                  String containing the path to the svg file

options:
  -h, --help            show this help message and exit
  -save_path SAVE_PATH  This argument is used to create the saving folder. It can either be a full path to chose the location of the  
                        directory or it can merely be a name. If the later is used, the folder will be created at the same location as
                        this python script
  -ksize kernel size    Kernel size for the gaussian blur apply in the image processing. Default is (3,3)
```
