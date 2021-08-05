import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import csv
import numpy as np
import pandas as pd
from glob import glob
import os
import scipy.signal
from matplotlib.font_manager import FontProperties
import sys

from datatools import fixGear, fixRPM, fixSPD, resetHistory

# Will only generate data for the first FRAME_LIMIT frames
FRAME_LIMIT = 5000 

# Applies the savgol filter if True
SMOOTHING = True

# Will "fix" the RPM, Gear, and SPD, at the last given value if they are unchanged for over FIX_TRESH frames
# Usefull if you just want to compare acceleration
# To disable set to 99999
FIX_TRESH = 99999

SAVE_FIXED_CSV = True

FIXED_FOLDER = "csv_fixed"
if SAVE_FIXED_CSV and not os.path.exists(FIXED_FOLDER):
    os.makedirs(FIXED_FOLDER)

fontP = FontProperties()
fontP.set_size('xx-small')
fig, axs = plt.subplots(3)

# We will plot each .csv file in the folder.
for file in glob("csv/*.csv"):
    name = os.path.basename(os.path.splitext(file)[0])
    history = [None]*FIX_TRESH
    data = []
    fix = False
    print(file)
    resetHistory()
    with open(file, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        header = next(csv_reader)
        if header != None:
            for i, row in enumerate(csv_reader):
                if row[0] == "N":
                    row[0] = 0
                row[1] = fixRPM(row[1])
                row[2] = fixSPD(row[2])
                try:
                    crow = [int(row[0]), int(row[1]), int(row[2])]
                    # We keep track of the current row, crow, and compare it to previous rows to see if the value should be locked
                    if fix == False and history[i % FIX_TRESH] == crow:
                        fix = crow
                        print(fix)
                    # Will fixate all following data points to be the same value (so deacceleration values are not displayed / used)
                    if fix:
                        data.append(fix)
                    else:
                        history[i % FIX_TRESH] = crow
                        data.append(crow)
                except Exception as e:
                    print("Err in line '{}': {} {}".format(i, row, e))
    if not fix:
        fix = crow
    if i < FRAME_LIMIT:
        for ii in range(i, FRAME_LIMIT):
            data.append(fix)

    # Precoress and transform the data for the plot
    data = np.array(data[:FRAME_LIMIT])
    
    if SAVE_FIXED_CSV:
        with open(os.path.join(FIXED_FOLDER, name+'.csv') , 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(["GEAR", "RPM", "SPD"]) # write header
            for row in data:
                spamwriter.writerow(row) # write header

    pdata = []
    try:
        pdata.append(data[:, 0])
        pdata.append(data[:, 1])
        pdata.append(data[:, 2])
    except Exception as e:
        print(data)
        print(e)

    # For better visual looks we can use the savgol filter
    if SMOOTHING:
        for i, val in enumerate(pdata):
            pdata[i] = scipy.signal.savgol_filter(pdata[i], 51, 3)

    # Plot the data

    axs[0].plot(pdata[0], label = name)
    #axs[0].set_title('Gear')
    axs[0].set(xlabel='Frame', ylabel='Gear')
    axs[0].grid(color='0.95')
    axs[0].legend(title='Vehicles', bbox_to_anchor=(1.01, 1), loc='upper left', prop=fontP)

    axs[1].plot(pdata[1], label = name)
    #axs[1].set_title('RPM')
    axs[1].set(xlabel='Frame', ylabel='RPM')
    axs[1].grid(color='0.95')

    axs[2].plot(pdata[2], label = name)
    #axs[2].set_title('SPD')
    axs[2].set(xlabel='Frame', ylabel='Speed (km/h)')
    axs[2].grid(color='0.95')


plt.show()