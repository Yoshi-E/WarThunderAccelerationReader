import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cbook as cbook
import csv
import pandas as pd
from glob import glob
import os
import scipy.signal
from matplotlib.font_manager import FontProperties
import sys

labels = ['Leopard 2A4', 'Leclerc2S', 'M1A2', "T-80U", 'Leopard 1', "Challenger 2"]
wt =     [260,                  258,     251,     243,          334,           353]
real =   [6,                      6,     7.5,     8.5,          9.5,            12]

for i, v in enumerate(wt):
    wt[i] = round(v/60, 1) 

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, wt, width, label='War Thunder')
rects2 = ax.bar(x + width/2, real, width, label='Real Trials / Official data')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Time in seconds')
ax.set_title('Acceleration of MBTs from 0 to 32km/h on asphalt')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

#ax.bar_label(rects1, padding=3)
#ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.show()