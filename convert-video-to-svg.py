'''
@author: yohan lanier
@date: 03/01/2022
@brief : a program loading a video using open cv. The video is processed frame by frame.
For each frame, contours are extracted using a Canny edge filtering process. Then each
each contour is saved as path in an as svg file. A folder is created to store the output for
processed each video. 
'''
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import imutils
import svgwrite
import os
from tqdm import tqdm
import argparse
from Exceptions import check_if_saving_directory_exists, check_if_input_file_exists, check_input_format
from tkinter import filedialog


canny_min = 100
canny_max = 200
canny_aperture = 3

def resize_image(src, scale_percent = 80):
    width = int(src.shape[1] * scale_percent / 100)
    height = int(src.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv2.resize(src, dim, interpolation = cv2.INTER_AREA)
    return resized

def extract_contours_sorted_by_area(edges):
    '''
    mere function which uses cv2 to extract contours from the canny edge output. Contours are then sorted by area

    input:
    ------------------------------------
            + edges: an opencv image corresponding to a frame of the output of the canny edge filter
    '''
    cnts, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_cnts = sorted(cnts, key=lambda x: cv2.contourArea(x), reverse=True)
    return sorted_cnts

def save_contours_as_svg(contours, svg_name):
    '''
    saves the detected contours as an svg file using the svgwrite package

    inputs:
    ---------------------------------------------------------
            + contours: list
                        a list containing all the detected contours, each contour is a list of point coordinates, see opencv doc on contour type
            + svg_name: string
                        name under which the svg file will be saved
    '''
    dwg = svgwrite.Drawing(svg_name, profile='full')
    for c in contours:
        style ="fill: none; stroke: #000000; stroke-width: 1.5; stroke-linecap: square"
        p = svgwrite.path.Path(d="M", style=style)
        for i in range(len(c)):
            x, y = c[i][0]
            if i == 0:
                p.push(x, y)
            else:
                p.push([(x, y)])
        dwg.add(p)
    dwg.save()
    return None

def deal_with_first_frame(frame, svg_name, blur_ksize = (3,3)):
    '''
    A function which allows for a calibration of the contour detection on the first frame of the video.
    Different parameters of the detection can be adjusted:
        + minimal threshold on canny edge detection
        + maximal threshold on canny edge detection
        + aperture parameter on canny edge detection

    inputs:
    -------------------------
        + frame: an opencv image corresponding to a frame of the analyzed video
        + svg_name: str
                    name used to save the detected contour as an svg file   
        + blur_ksize: tuple, optional
                      size of the kernel used to apply gaussian blur in the pre-processing of the images 
    '''
    #first convert to grayscale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #then reduce noise in the frame
    img_blur = cv2.GaussianBlur(gray, blur_ksize, 0)
    #display gray image
    cv2.imshow('gray image of first frame', img_blur)
    print('--------------------------------------------------------')
    print("The first frame your video is displayed using opencv. Press the space bar to extract contours")
    cv2.waitKey(0)
    edges = cv2.Canny(img_blur, threshold1 = canny_min, threshold2 = canny_max, apertureSize = canny_aperture)
    cv2.imshow('canny edge on first frame', edges)
    #---------------------------------------------------------------------------
    #Callback for min value
    def canny_min_callback(val):
        global canny_min, canny_max
        canny_min = val
        #maintain a difference between min and max
        if canny_min >= canny_max:
            canny_max = canny_min+20
            if canny_max >= 1000:
                canny_max=1000
            cv2.setTrackbarPos('Canny max', 'Controls', canny_max)
        edges = cv2.Canny(img_blur, threshold1 = canny_min, threshold2 = canny_max, apertureSize = canny_aperture)
        cv2.imshow('canny edge on first frame', edges)
    #Callback for max value
    def canny_max_callback(val):
        global canny_min, canny_max
        canny_max = val
        if canny_max <= canny_min:
            canny_min = canny_max-20
            if canny_min <= 0:
                canny_min=0
            cv2.setTrackbarPos('Canny min', 'Controls', canny_min)
        edges = cv2.Canny(img_blur, threshold1 = canny_min, threshold2 = canny_max, apertureSize = canny_aperture)
        cv2.imshow('canny edge on first frame', edges)
    #Callback for aperture value
    def canny_aperture_callback(val):
        global canny_aperture
        #aperture value can only be odd between 3 and 7
        if val == 4:
            val = 5
            cv2.setTrackbarPos('Canny aperture', 'Controls', val)
        elif val == 6:
            val = 7
            cv2.setTrackbarPos('Canny aperture', 'Controls', val)
        canny_aperture = val
        edges = cv2.Canny(img_blur, threshold1 = canny_min, threshold2 = canny_max, apertureSize = canny_aperture)
        cv2.imshow('canny edge on first frame', edges)
    #---------------------------------------------------------------------------
    #create control window
    cv2.namedWindow('Controls')
    cv2.createTrackbar('Canny min', 'Controls', 100, 1000, canny_min_callback)
    cv2.createTrackbar('Canny max', 'Controls', 200, 1000, canny_max_callback)
    cv2.createTrackbar('Canny aperture', 'Controls', 3, 7, canny_aperture_callback)
    cv2.setTrackbarMin('Canny aperture', 'Controls', 3)
    print('--------------------------------------------------------')
    print("Extracted contour is displayed using opencv. You can use the sliders to calibrate the detection of the first frame. The settings will be saved for all the other frames (this assumes the contrast remains even trhough the video). Press space when you are satisfied with values.")

    cv2.waitKey(0)
    #destroy windows
    cv2.destroyAllWindows()
    #extract contours
    sorted_contours = extract_contours_sorted_by_area(edges)
    if len(sorted_contours)==0:
        return 0
    #saeve contours into an svg file
    save_contours_as_svg(sorted_contours, svg_name)
    return

def deal_with_a_frame(frame, svg_name, canny_min, canny_max, canny_aperture, blur_ksize = (3,3)):
    '''
    inputs:
    -------------------------
        + frame: an opencv image corresponding to a frame of the analyzed video
        + svg_name: string used to save the frame's contours as an svg
        + canny_min: int used to delete edges below threshold in canny edge detection
        + canny max: int used to keep edges above this threshold in canny edge detection
        + canny aperture: int, between 3 and 7, controls the amount of details detected by canny edge filtering
        + blur_ksize: tuple, optional, controls the size of Gaussian kernel for image blurring
    '''
    #first convert to grayscale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #then reduce noise in the frame
    img_blur = cv2.GaussianBlur(gray, blur_ksize, 0)
    #apply canny edge detection to blurred image
    edges = cv2.Canny(img_blur, threshold1 = canny_min, threshold2 = canny_max, apertureSize = canny_aperture)
    #extract contours
    sorted_contours = extract_contours_sorted_by_area(edges)
    if len(sorted_contours)==0:
        return 0
    #saeve contours into an svg file
    save_contours_as_svg(sorted_contours, svg_name)
    return

def process_video(video_name, save_name, blur_ksize = (3,3)):
    '''
    Opens a video and loops over each frame to extract its contours as an individual svg file which
    is saved in a directory using the save_name parameter

    inputs :
    -------------------------------------------------------------------------
        + video_name: str
                      path to the video to process
        + save_name: str
                     name used to create the saving directory. If a directory with this names already exists, program fails. 
        + blur_ksize: tuple, optional
                      size of the kernel used to apply gaussian blur in the pre-processing of the images
    '''
    #open video
    video = cv2.VideoCapture(video_name)
    nb_frame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    #go through all frames
    for i_frame in tqdm(range(nb_frame), desc='Progression of frame processing'):
        if video.isOpened():
            ret, frame = video.read()
            frame = resize_image(frame, scale_percent = 70)
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            #setting parameters on first frame
            if i_frame == 0:
                check = deal_with_first_frame(frame, save_name+f'/svg_frame_{i_frame}.svg', blur_ksize = blur_ksize)
            #processing the rest of the frames
            else:
                check = deal_with_a_frame(frame, save_name+f'/svg_frame_{i_frame}.svg', canny_min, canny_max, canny_aperture, blur_ksize=blur_ksize)
            if check == 0:
                print(f'no contour extracted in frame {i_frame}')
    #close everything properly
    video.release()
    cv2.destroyAllWindows()
    return

def main_python_command_line(args):
    file = args['file']
    save_path = args['save_path']
    ksize = args['ksize']
    file = check_if_input_file_exists(file)
    file = check_input_format(file)
    #Check if saving directory already exists or not
    save_path = check_if_saving_directory_exists(save_path)
    #create saving directory
    os.mkdir(save_path)
    process_video(file, save_path, blur_ksize = ksize)

def main_app():
    print('--------------------------------------------------------')
    print("Welcome in the app, first selet a video file to process, then select the location at which the saving directory will be created")
    print('--------------------------------------------------------')
    file = filedialog.askopenfile().name
    #check if input file exists and if it has a supported format
    file = check_if_input_file_exists(file)
    file = check_input_format(file)
    saving_location = filedialog.askdirectory()
    print('--------------------------------------------------------')
    print('Input the name for the saving directory of your project:')
    save_dir_name = input()
    save_path = saving_location+'/'+save_dir_name
    #Check if saving directory already exists or not
    save_path = check_if_saving_directory_exists(save_path)
    #create saving directory
    os.mkdir(save_path)

    print('--------------------------------------------------------')
    input('Saving directory successfully created, press enter to continue')

    process_video(file, save_path)
    print('--------------------------------------------------------')
    print('video successfully processed ! ')
    print(""""                                                                                                                                                                                                                                                         
        
                                              
   (                                    )     
   )\               (  (  (       )  ( /(     
 (((_)   (    (     )\))( )(   ( /(  )\())(   
 )\___   )\   )\ ) ((_))\(()\  )(_))(_))/ )\  
((/ __| ((_) _(_/(  (()(_)((_)((_)_ | |_ ((_) 
 | (__ / _ \| ' \))/ _` || '_|/ _` ||  _|(_-< 
  \___|\___/|_||_| \__, ||_|  \__,_| \__|/__/ 
                   |___/                      
""")

if __name__ == '__main__':
    #Uncomment following lines to use command line version
    #----------------------------------------
    # arguments = argparse.ArgumentParser()
    # arguments.add_argument('file', help ='String containing the path to the svg file')
    # arguments.add_argument('-save_path', type = str, help = 'This argument is used to create the saving folder. It can either be a full path to chose the location of the directory or it can merely be a name. If the later is used, the folder will be created at the same location as this python script' )
    # arguments.add_argument('-ksize', metavar = 'kernel size', default = (3,3), help = 'Kernel size for the gaussian blur apply in the image processing. Default is (3,3)')
    # args = vars(arguments.parse_args())
    # main_python_command_line(args)
    #----------------------------------------
    main_app()