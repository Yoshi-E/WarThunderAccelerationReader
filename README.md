# WarThunderAccelerationReader
Converts War Thunder mp4 videos into .csv acceleration data (Gear, RPM, Speed) on a per frame basis 

# Requirements:
Install with pip:
```pip install -r requirements.txt```

# How it works
1. This tools reads a Video frame by frame.
2. For each frame it looks at the numbers for current Gear, Engine RPM and Speed.
3. The numbers are detected via distance based image hashing, and references a folder based database.
4. Images that could not be mached will be stored.
5. Once a speed over 0km/h is detected, the data will be written to a .csv file with the same name as the video file.

# Files
The tools are configured with constants inside the files.

`detect.py` Runs the detection on the configured video file

`datatools.py` Provides auxiliary functions for plot.py

`plot.py` Plots data from the generated .csv files. Will also correct incorrect readings.

# Examples
In the example folder you will find example .csv files and example hash databases for different resolutions.
Hoverever I do recommend to generate everything yourself.

# How to use the detector
1. After downloading you first have to configure `detect.py`
   *  Set the constant `VIDEO` to match the video resoltion (Currently only 1080p and 2k is supported)
   *  Set the path to the video file you want to use for the detection with `VIDEOFILE` 
2. Run `detect.py` once and ensure that it runs without error
   *  In the console the script should display something like this: 
   *  ```[    1] Gear: None RPM: None SPD: None```
   *  This is because it has not found any hash database yet
3. After running it, `detect.py` should have created a "hashes" folder with multiple sub folder, and should have populated it with many small images
   * ![Setup](/examples/setup1.png?raw=true)
   * Should the number of images exceed 500, I would recommend to increase the `TRESH`
4. Now you have to sort each image to the respective folder like this:
   * ![Setup](/examples/setup2.png?raw=true)
   * All images that do not clearly show the numbers 0-9 or the letter "N" should be placed in the "err" folder
5. Now rerun `detect.py`
   *  In the console the script should display something like this: 
   *  ```[   1] Gear: N RPM: 800  SPD: 0```
   *  ```[   2] Gear: N RPM: 800  SPD: 0```
6. Once you are done, that data should be saved in `csv/VIDEOFILE.csv`
   * The first datapoint in the .csv file is the frame before the first gear change is detected. (First instance of gear not being in neutral, "N").
   For exmample if in the orignal video the Vehicle is in "N" at frame 1000, and "Gear 1" at Frame 1001, the first row in the .csv would be frame 1000. 
   * Each data row represents one frame of the video.
7. Every time you run a new video, you have to check for new unsorted images in the hashes folder. Otherwise it can cause incorrect readings.

# How to use the plotter:
1. Configure the variables in `plot.py` to your needs
2. Run `plot.py` to generate a plot with all .cvs files
The result should look something like this:
![Setup](/examples/Figure_1_smoothed.png?raw=true)
