# -*- coding: utf-8 -*-
"""
Created on Mon, Jun 25 2018

This script is to convert YOLOv2 annotations into CSV files for use to generate TFRecord.
Modified based on code found here: https://github.com/datitran/raccoon_dataset/blob/master/xml_to_csv.py

Example usage: python convert_yolov2_to_csv.py -d annotations

#YOLOv2 format:
Line 1:[category number] [object center in X] [object center in Y] [object width in X] [object width in Y]

## Where x, y, width, and height are relative to the image's width and height.
## <class_number> (<absolute_x> / <image_width>) (<absolute_y> / <image_height>) (<absolute_width> / <image_width>) (<absolute_height> / <image_height>)

#BBox label tool format:
Line 1:[category number]
Line 2:[bounding box left X] [bounding box top Y] [bounding box right X] [bounding box bottom Y]

@author: Wilson Ow
Email: wilsonxin@kimo.com
"""

import os
import glob
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

from PIL import Image
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-d", "--directory", dest="directory",
                    help="directory which contains YOLOv2 annotations txt files", metavar="DIR")
parser.add_argument("-i", "--image_directory", dest="image_directory",
                    help="directory which contains image files", metavar="DIR")

args = parser.parse_args()

def image_object_class(x):
    # return object class name as it is digit in yolov2 format
    # this is the wannabe-switch-case equivalent of java
    return {
        0: 'funnel',
        1: 'wrench',
        2: 'generator'
    }.get(x, 'funnel')    # 9 is default if x not found

def filename_without_extension(filename):
    # split full path filename into head and tail
    head, tail = os.path.split(filename)
    return tail.replace(".txt", "")

def yolov2_to_csv(annotation_path, image_path):
    xml_list = []
    # loop and find each and every txt annotation file
    for yolov2_file in glob.glob(annotation_path + '/*.txt'):

        # get filename without extension
        filename = filename_without_extension(yolov2_file)
        # Uncomment below to display annotation file name
        #print('File: ' + filename + '.txt')
        # open image to get image size
        im = Image.open(os.path.join(image_path, filename + '.jpg'))
        img_width, img_height = im.size
        # Uncomment below to display matching image name and size
        #print('Matching image: ' + im.filename + ' width: ' + str(img_width) + ' height: ' + str(img_height))

        # open and read current looped txt annotation file
        with open(yolov2_file, 'rt') as fd:

            # convert variable to float
            img_width = float(img_width)
            img_height = float(img_height)
            first_line = fd.readline()
            # split values into array and convert to float
            elems = [float(x) for x in first_line.split(' ')]
            # read annotations into value variable
            box_width = elems[3] * img_width
            box_height = elems[4] * img_height
            # absolute (x,y) for center
            absolute_x = elems[1] * img_width
            absolute_y = elems[2] * img_height
            # (x,y) coordinates required for generating csv
            xmin = absolute_x - (box_width / 2)
            ymin = absolute_y - (box_height / 2)
            xmax = absolute_x + (box_width / 2)
            ymax = absolute_y + (box_height / 2)

            value = (filename_without_extension(im.filename),
                    int(box_width),
                    int(box_height),
                    image_object_class(int(elems[0])),
                    int(xmin),
                    int(ymin),
                    int(xmax),
                    int(ymax)
                    )

        xml_list.append(value)
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main():

    image_path = os.path.join(os.getcwd(), args.image_directory)
    annotation_path = os.path.join(os.getcwd(), args.directory)
    yolov2_df = yolov2_to_csv(annotation_path, image_path)
    yolov2_df.to_csv('labels.csv', index=None)
    print('Successfully converted xml to csv.')


main()
