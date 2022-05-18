import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import time
import os
import cv2
import statistics
from datetime import datetime
import textwrap

root = tk.Tk()
root.withdraw()

folder_path = filedialog.askdirectory()
print(folder_path)
now = datetime.now()

video_name = f"{os.path.basename(folder_path)}_PROC{now.strftime('%Y-%m-%d-%H-%M-%S')}.avi"
outputfile = os.path.join(folder_path, video_name)
images = [img for img in os.listdir(folder_path) if img.endswith(".tiff") or img.endswith(".png") or img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".bmp")]
if not images:
    messagebox.showerror("No images", "No images with extension '.tiff', '.png', '.jpg', '.jpeg' or '.bmp' found in selected folder.")
    raise Exception("No images with extension '.tiff', '.png', '.jpg', '.jpeg' or '.bmp' found in selected folder.")

referenceFrame = cv2.imread(os.path.join(folder_path, images[0]))
(referenceHeight, referenceWidth, referenceLayers) = referenceFrame.shape

for idx, image in enumerate(images):
    frame = cv2.imread(os.path.join(folder_path, image))
    if frame is None or (referenceHeight, referenceWidth, referenceLayers) != frame.shape:
        messagebox.showerror("Invalid images", f"Not possible to create timelapse. All images need to be of same shape. Image '{image}' has a different shape than the first image '{images[0]}'.")
        raise Exception(f"Not possible to create timelapse. All images need to be of same shape. Image '{image}' has a different shape than the first image '{images[0]}'.")


input_framerate = simpledialog.askfloat('Recording FPS', 'Input the recording frame rate', minvalue=0)
output_framerate = simpledialog.askinteger('Output FPS', 'Input the video output frame rate', minvalue=1, maxvalue=120, initialvalue=15)



# TODO variable fps!
video = cv2.VideoWriter(outputfile, 0, output_framerate, (referenceWidth, referenceHeight))


fontSizeRatio = 6 / 3000
font = cv2.FONT_HERSHEY_SIMPLEX
locationTime = (50, 180)
locationName = (750, 100)
locationRundatetime = (750, 160)
locationCurrent = (50, referenceHeight - 20)
fontScale = referenceHeight * fontSizeRatio
fontColor = (255, 255, 255)
thickness = 10
lineType = 3


def TimeRemaining(arraytimes, left):
    avgtime = statistics.mean(arraytimes)
    timeremaining = left * avgtime
    if timeremaining < 2:
        rem = f"1 second"
    elif timeremaining < 90:
        rem = f"{round(timeremaining)} seconds"
    elif timeremaining < 3600:
        rem = f"{round(timeremaining / 60)} minutes"
    else:
        rem = f"{round(timeremaining / 3600)} hours"
    print(f"Estimated time remaining: {rem}")
    return True


def FancyTimeFormat(t, max_t, mode='variable'):
    if mode == 'variable':
        if t < 90:
            out = f"{round(t)}s"
        elif t < 3600:
            out = f"{round(t / 60)}min"
        else:
            out = f"{round(t / 3600)}hrs"
    elif mode == 'auto':
        if max_t < 90:
            out = f"{round(t)}s"
        elif max_t < 3600:
            out = f"{round(t / 60)}min"
        else:
            out = f"{round(t / 3600)}hrs"
    elif mode == 'sec':
        out = f"{round(t)}s"
    elif mode == 'min':
        out = f"{round(t / 60)}min"
    elif mode == 'hrs':
        out = f"{round(t / 3600)}hrs"
    else:
        ValueError(f'{mode} is not a valid option. try variable, auto, sec, min or hrs.')
    return out

originalPath = textwrap.wrap(f"Original path: {folder_path}", width=100)
nowstr = now.strftime('%d-%m-%Y, %H:%M:%S')

timetracker = []
for idx, image in enumerate(images):
    start = time.time()
    img = cv2.imread(os.path.join(folder_path, image))

    cv2.putText(img, f"t={FancyTimeFormat(input_framerate * idx, len(images), mode='auto')}",
                locationTime, font, fontScale, fontColor, thickness, lineType)
    for i, line in enumerate(originalPath):
        offset = i * (fontScale * 10)
        loc = (locationName[0], round(locationName[1] + offset))
        cv2.putText(img, line, loc, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)

    locationRundatetime = (locationRundatetime[0], round(loc[1] + offset))
    cv2.putText(img, f"Video created: {nowstr}",
                locationRundatetime, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)
    cv2.putText(img, f"{image}",
                locationCurrent, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)


    video.write(img)
    timetracker.append(time.time() - start)
    TimeRemaining(timetracker, len(images) - idx)



cv2.destroyAllWindows()
video.release()