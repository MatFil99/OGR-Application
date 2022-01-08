import cv2 as cv
import numpy as np

from .share import *

def preprocess(source_img, user_params: UserParams):
    """
    First step of Optical Graph Recognition is to prepare image:
    """

    resized = resize(source_img)
    gray_img = convert_to_grayscale(resized, user_params.in_img_type, user_params.bg_brightness)
    clean_gray = grayscale_denoising(gray_img)
    binary = convert_to_binary(clean_gray, user_params.in_img_type)
    extended_bin = extend_binary(binary)
    clean_binary = binary_denoising(extended_bin)
    
    return clean_binary

def extend_binary(binary):
    """"""
    offset = 5
    result = np.zeros((binary.shape[0] + 2*offset, binary.shape[1] + 2*offset), np.uint8)
    result[offset:result.shape[0]-offset, offset:result.shape[1]-offset] = binary

    return result

def resize(img, maxwidth=Options.MAXWIDTH, maxheight=Options.MAXHEIGHT):
    """
    Resize image to simplify recognition

    """

    if img.shape[0] > img.shape[1]:
        img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)

    if img.shape[1]/img.shape[0] > maxwidth/maxheight:
        factor = maxwidth / img.shape[1]
    else:
        factor = maxheight / img.shape[0]

    result = cv.resize(img, (0,0), fx=factor, fy=factor)
    return result

def convert_to_grayscale(image, in_img_type = UserParams.InImgType.PHOTO_IMG, bg_brightness = None):
    """
    convert BGR image to grayscale image 
    represent background by bright color (white) and graph by dark (black) 
    """
    
    grayscale_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    if not bg_brightness:
        mean_brightness = np.average(grayscale_img)
        median_brightness = np.median(grayscale_img)

        min_brightness = np.min(grayscale_img)
        max_brightness = np.max(grayscale_img)
        minmax_avg_brightness = min_brightness/2 + max_brightness/2

        if in_img_type == UserParams.InImgType.PHOTO_IMG:
            if median_brightness < mean_brightness:
                grayscale_img = cv.bitwise_not(grayscale_img)

        if in_img_type == UserParams.InImgType.COMPUTER_IMG:
            if median_brightness < minmax_avg_brightness:
                grayscale_img = cv.bitwise_not(grayscale_img)
    else:
        if bg_brightness == UserParams.BgBrightness.BG_DARK:
            grayscale_img = cv.bitwise_not(grayscale_img)

    return grayscale_img

def grayscale_denoising(gray_img, h=5, tWS=7, sWS=21):
    """
    removes noises from grayscale image
    h - 	Parameter regulating filter strength. Big h value perfectly removes noise but also removes 
            image details, smaller h value preserves details but also preserves some noise
    tWS -   (templateWindowSize) Size in pixels of the template patch that is used to compute weights. Should be odd. 
            Recommended value 7 pixels
    sWS -   (searchWindowSize) Size in pixels of the window that is used to compute weighted average for given pixel. 
            Should be odd. Affect performance linearly: greater searchWindowsSize - greater denoising time. 
            Recommended value 21 pixels
    """

    clean_gray = cv.fastNlMeansDenoising(gray_img, h = h, templateWindowSize=tWS, searchWindowSize=sWS)

    return clean_gray

def convert_to_binary(gray_img, in_img_type=UserParams.InImgType.PHOTO_IMG, block_size=5, c=2):
    """
    converting grayscale image to binary image (only black and white colors)
    it uses thresholding - adaptive, because it works better with brightness difference of different 
    parts of the picture (especially photos)

    returns binary picture which objects are white and background black
    """
    thresh_type = cv.THRESH_BINARY_INV

    if in_img_type == UserParams.InImgType.PHOTO_IMG:
        binary = cv.adaptiveThreshold(gray_img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, \
            thresh_type, blockSize=block_size, C=c)
    else:
        mean_brightness = np.mean(gray_img)
        _, binary = cv.threshold(gray_img, mean_brightness, 255, thresh_type)

    return binary

def binary_denoising(binary_img, h=Options.MAXNOISE):
    """
    removes noise - next removes small contours (pics)
    """
    
    clean_bin = np.zeros((binary_img.shape[0], binary_img.shape[1], 1), np.uint8)
    contours, hierarchy = cv.findContours(binary_img, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE) # CHAIN_APPROX_SIMPLE

    clean_contours = list()
    it = 0
    for cnt in contours:

        if len(cnt) > h :
            clean_contours.append(cnt)
            it+=1

    cv.drawContours(clean_bin, clean_contours, -1, color=Color.WHITE, thickness=cv.FILLED)

    return clean_bin