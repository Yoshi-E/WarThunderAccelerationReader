import numpy as np
import imagehash
from PIL import Image, ImageChops, ImageStat
import os
from glob import glob
from random import randint
import cv2
import csv
import sys
import random

# Quickly select the selected resolution:
VIDEO = "1080p"

# Location of the VIDEO file
VIDEOFILE = 'videos/test2.mp4'

# Configure the region selection for the given snipets.
# Best practise is to determin the position of the elemtents from a screenshot of the desired resolution.
# Format: (x,y,w,h)
if VIDEO == "1080p":
    HASHFOLDER = "hashes_1080p"
    GEAR = (67, 1004, 35, 22)
    RPM = (59, 1023, 57, 22)
    SPD = (56, 1042, 48, 22)
elif VIDEO == "1080p on 2k":
    HASHFOLDER = "hashes_upscaled"
    #HASHFOLDER = "hashes_red_upscaled"
    GEAR = (88, 1340, 35, 22)
    RPM = (79, 1366, 56, 22)
    SPD = (74, 1391, 48, 22)
elif VIDEO == "2k native":
    HASHFOLDER = "hashes_2k"
    GEAR = (84, 1346, 35, 22)
    RPM = (75, 1371, 56, 22)
    SPD = (71, 1396, 48, 22)


# Position of the first 4 digits in the cropped snippets (GEAR, RPM, SPD):
# Format: (x,y,w,h)
if "2k" in VIDEO: #2k res
    DIGITS = [(1, 2, 14, 19),
            (14, 2, 14, 19),
            (27, 2, 14, 19),
            (40, 2, 14, 19)]
    # HASH Diffrence Theshhold 
    # Lower Number: More sensetive --> More hash images need to be stored
    # Higher Number: Less sensetive, but it will be possible for numbers to be mistake for one another
    TRESH = 10  
else: #1080p
    DIGITS = [(1, 2, 11, 15),
            (11, 2, 11, 15),
            (20, 2, 11, 15),
            (30, 2, 11, 15)]
    TRESH = 8 # As the sections are smaller, we also need to reduce the error tolerance  


# HASH_SIZE: Bit size of the image hash. 
# Larger HASH_SIZE increses computation complexity, but also make the algorithm more sensetive to difference between images.
# It is recommended not to change this value
HASH_SIZE = 8 


# Debugging
# Will display each cropped image (test if the crops are set correctly)
DEBUG = False

if not os.path.exists(HASHFOLDER):
    os.makedirs(HASHFOLDER)
    
if not os.path.exists("csv"):
    os.makedirs("csv")

for folder in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "err", "N"]:
    if not os.path.exists(os.path.join(HASHFOLDER, folder)):
        os.makedirs(os.path.join(HASHFOLDER, folder))

# Simple helper function to return an image subsection (crop).
# Input image is not modified.
def crop(image, x, y, w, h):
    return image[y:y+h, x:x+w]

# To make the detection process easier, it is first made black and white,
# and with some clever contrasting and filtering, we can remove most of the noise.
# Will fail if the numbers have a low contrast to the background, or are of a diffrent color than black / white
def pre_process_img(img):
    if "2k" in VIDEO:
        tresh = 70
    else:
        tresh = 20

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray, img_bin = cv2.threshold(gray,128,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    gray = cv2.bitwise_not(img_bin)

    kernel = np.ones((2, 1), np.uint8)
    img = cv2.erode(gray, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    # To remove noise we search for small patches of pixels, that are not connected to the largest patch.
    # All smaller patches will be removed (filled with nothing)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for i, cnt in enumerate(contours):
        # if the contour has no other contours inside of it
        contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) # Use cv2.CCOMP for two level hierarchy
        if cv2.contourArea(cnt) < tresh:
            # Fill the holes in the original image
            cv2.drawContours(img, [cnt], 0, (255), -1)
    return img

# Because for missile carries in War Thunder the numbers will be displayed red above a certain speed, we need to account for that.
# This function takes and input image, and mask all the red pixels to a white color
def maskRed(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    # Define lower and uppper limits of what we call "red"
    red_lo=np.array([0,80,80])
    red_hi=np.array([255,255,255])

    # Mask image to only select red
    mask=cv2.inRange(hsv,red_lo,red_hi)

    # Change image to white where we found red
    img[mask>0]=(255,255,255)
    return img

# Compares the hash of a given image to the hashes in the database.
# The distance and the hash of clostest match will be returned.
def find_closest_hash(hash):
    global hashMap
    hashes = []
    for key, item in hashMap.items():
        if item[1]:
            hashes.append(item[1])

    closest = None
    dis = 99999
    for e in hashes:
        distance = e-hash
        if distance < dis:
            dis = distance
            closest = e
    return dis, str(closest)

# An alternative implementation to calculate the hash distance via Hamming distance.
# However this is insenstive to larger in place differences, and is therefore not used at the moment. 
def find_closest_hash_hamming(hash_):
    global hashMap
    hamming_dists = []
    
    for map_hash in hashMap.values():
        hamming_dists.append(sum(c1 != c2 for c1, c2 in zip(str(hash_), str(map_hash[1]))))
    if hamming_dists:
        match_dist = min(hamming_dists)
        match = list(hashMap.keys())[hamming_dists.index(match_dist)]
        return match_dist, match
    return 999999, None

# To lookup similar hashes we first have to load them from the selected HASHFOLDER
# The name of the subfolder of a give hash will represent its mapped value.
# Images not in a sub folder, or in the sub folder "err" will be mapped to the value 'None'
def loadHashmap():
    global hashMap
    for file in glob(HASHFOLDER+"/*/*.png"):
        folder = os.path.basename(os.path.dirname(file))

        img = Image.open(file)
        rawhash = imagehash.phash(img, hash_size=HASH_SIZE)

        hash = os.path.basename(os.path.splitext(file)[0])
        hashMap[hash] = (folder, rawhash)

# Tries to read the value of an input image and returns it.
# Should it fail to find a match within the tresh value, it will return None, and save it to the HASHFOLDER
# Returns either None or String
def getVal(img, dir, tresh=10):
    global hashMap

    pil_img = Image.fromarray(img)
    rawhash = imagehash.phash(pil_img, hash_size=HASH_SIZE)
    hash = str(rawhash)

    distance, chash = find_closest_hash(rawhash)

    print(distance, chash, rawhash)
    if distance >= tresh:
        hashMap[hash] = (None, rawhash)
        pil_img.save(dir+"/"+hash+".png")
    else:
        return hashMap[chash][0]
    return None 


# Breaks down a snippet of a full number into individual digits.
# The digits are combined and returned as a combined String
# Will return partial readings
# Return None should it fail to read any value
def getValDigits(rawimg, _type, tresh=10):
    global hashMap
    value = ""
    if DEBUG:
        d = Image.fromarray(rawimg)
        d.save(_type+".png")

    for i, digit in enumerate(DIGITS):
        img = crop(rawimg, *digit)
        # Used for debugging: Are the numbers displayed correctly?
        if DEBUG:
            cv2.imshow("Input", img)
            cv2.waitKey(0)
        pil_img = Image.fromarray(img)
        rawhash = imagehash.phash(pil_img, hash_size=HASH_SIZE)
        hash = str(rawhash)
        distance, chash = find_closest_hash(rawhash)
        if distance >= tresh:
            hashMap[hash] = (None, rawhash)
            pil_img.save(os.path.join(HASHFOLDER, hash+".png"))
        else:
            if hashMap[chash][0] and hashMap[chash][0] != "err":
                value += hashMap[chash][0]
        if _type=="gear": # limit to only 1 digit (afaik, there are no 2 digit gears in WT)
            break        
        if _type=="spd" and i==2: # limit to 3 digits (We do not care about speeds >999km/h)
            break
    if value:
        return value
    # Used for debugging: Save incorrectly recognized hashes to an extra folder
    #pil_img = Image.fromarray(rawimg)
    #pil_img.save("hashes_err/{}.png".format(random.randint(0,99999999)))
    #cv2.imshow("Input", rawimg)
    #cv2.waitKey(0)
    return None
    
hashMap = {}
previous_row = None

loadHashmap()

if __name__ == "__main__":
    vidcap = cv2.VideoCapture(VIDEOFILE)
    success,frame = vidcap.read() # read the first frame of the video
    frame_i = 1
    with open(f'csv/{os.path.basename(VIDEOFILE)}.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["GEAR", "RPM", "SPD"]) # write header

        # As long as we have a valid video frame, attempt to read the numbers and write it to a csv file.
        while success: 
            snip = crop(frame, *GEAR)
            gimg = pre_process_img(snip)
            gear = getValDigits(gimg, "gear", tresh=TRESH)

            snip = crop(frame, *RPM)
            rimg = pre_process_img(snip)
            rpm = getValDigits(rimg, "rpm", tresh=TRESH)

            snip = crop(frame, *SPD)
            snip = maskRed(snip) # handels "red numbers" for the speed indicator
            simg = pre_process_img(snip)
            spd = getValDigits(simg, "spd", tresh=TRESH)

            try:
                print("[{: >4}] Gear: {} RPM: {: <4} SPD: {: <3}".format(frame_i, gear, rpm, spd))
            except:
                print("[{: >4}] Gear: {} RPM: {} SPD: {}".format(frame_i, gear, rpm, spd))

            if gear != "N" or spd!="0":
                try:
                    spamwriter.writerow(previous_row)
                except Exception as e:
                    spamwriter.writerow([0,0,0]) #writes empty data on error
                    print(e)
            previous_row = [gear, rpm, spd]
            success,frame = vidcap.read()
            frame_i += 1
    # cv2.imshow("Input", frame)
    # cv2.waitKey(0)