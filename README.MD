## Simple Timelapse Assembler

This GUI program creates simple timelapses from images (.tiff, .png, .jpg, .jpeg, .bmp).<br>
Executable can be found in `dist`.

There are 2 main workflows:
- Create a simple .mp4 movie from images (with or without overlay). Input fps, output fps and compression rate can be set. The overlay includes: time, filenames, folder name. Input fps is only relevant if the overlay is turned on. Note that only fixed fps videos can be processed for now.
- Create a .avi rawvideo (not playable in VLC) for the OCA, which requires specific codecs. The output video height can be set or calculated automatically (recommended). Videos that are too high don't fit the OCA software screen, videos that are too large can't be opened. With `Calculate max height` you can be sure it will open. Note that no progress is shown with this mode; large image stacks take several minutes.

Video can be manually overlayed with temperature information

Default settings for the program are saved with `Set settings as default` to a json file.

## Executable Windows Defender Issues
If Windows tries to Defend you from using this programn, check the following:
- make sure you are administrator of the device
- right-click the executable, and go to 'properties'. There, in the 'General' tab, tick the 'Unblock' box at the bottom. The programn should run without issues now.

<img src="screenshots\img.png" align="center" width="80%" />