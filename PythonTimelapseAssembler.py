import time
import os
import cv2
import statistics
from datetime import datetime
import textwrap
import numpy as np
from natsort import natsorted

# executable created via Terminal in Pycharm: pyinstaller -F PythonTimelapseAssembler.py

def TimeRemaining(arraytimes, left):
    avgtime = statistics.mean(arraytimes)
    timeremaining = left * avgtime
    if timeremaining < 2:
        rem = f"Almost done now ..."
    elif timeremaining < 90:
        rem = f"{round(timeremaining)} seconds"
    elif timeremaining < 3600:
        rem = f"{round(timeremaining / 60)} minutes"
    else:
        rem = f"{round(timeremaining / 3600)} hours"
    print(f"{datetime.now().strftime('%H:%M:%S')} Estimated time remaining: {rem}")
    return True


def FancyTimeFormat(t, max_t, mode='variable'):
    if mode == 'variable':
        if max_t < 5:
            out = f"{round(t * 1000)}ms"
        elif t < 90:
            out = f"{round(t)}s"
        elif t < 3600:
            out = f"{round(t / 60)}min"
        else:
            out = f"{round(t / 3600)}hrs"
    elif mode == 'auto':
        if max_t < 5:
            out = f"{round(t * 1000)}ms"
        elif max_t < 90:
            out = f"{round(t)}s"
        elif max_t < 3600:
            out = f"{round(t / 60)}min"
        else:
            out = f"{round(t / 3600)}hrs"
    elif mode == 'ms':
        out = f"{round(t * 1000)}ms"
    elif mode == 'sec':
        out = f"{round(t)}s"
    elif mode == 'min':
        out = f"{round(t / 60)}min"
    elif mode == 'hrs':
        out = f"{round(t / 3600)}hrs"
    else:
        ValueError(f"{datetime.now().strftime('%H:%M:%S')} {mode} is not a valid option. try variable, auto, sec, min or hrs.")
    return out

def timestamps_to_deltat(timestamps):
    deltat = [0]
    for idx in range(1, len(timestamps)):
        deltat.append((timestamps[idx] - timestamps[idx - 1]).total_seconds())
    return deltat

def get_timestamps(filenames_fullpath, method, input_fps=False):
    if method == 'Fixed':
        # deltatime = np.arange(0, len(filenames_fullpath)) * input_fps
        deltatime = np.ones(len(filenames_fullpath)) * input_fps
    elif method == 'Read from creation date (Windows only)':
        timestamps = []
        for f in filenames_fullpath:
            timestamps.append(datetime.fromtimestamp(os.path.getctime(f)))
        deltatime = timestamps_to_deltat(timestamps)
    elif method == 'Read from modified date (Windows only)':
        timestamps = []
        for f in filenames_fullpath:
            timestamps.append(datetime.fromtimestamp(os.path.getmtime(f)))
        deltatime = timestamps_to_deltat(timestamps)
    elif method == 'Read from filename':
        deltatime = []
        # timestamps = []
        # for f in filenames:
        #     # match = re.search(r"[0-9]{14}", f)  # we are looking for 14 digit number
        #     match = re.search(config.get("GENERAL", "FILE_TIMESTAMPFORMAT_RE"), f)  # we are looking for 14 digit number
        #     if not match:
        #         logging.error("No 14-digit timestamp found in filename.")
        #         50()
        #     try:
        #         timestamps.append(datetime.strptime(match.group(0), config.get("GENERAL", "FILE_TIMESTAMPFORMAT")))
        #     except:
        #         exit()
        # deltatime = timestamps_to_deltat(timestamps)
    return deltatime

def validate_images(analyze_images, images, folder_path, inputHeight, inputWidth, referenceLayers):
    for idx in analyze_images:
        image = images[idx]
        frame = cv2.imread(os.path.join(folder_path, image))
        if frame is None or (inputHeight, inputWidth, referenceLayers) != frame.shape:
            raise Exception(f"{datetime.now().strftime('%H:%M:%S')} Not possible to create timelapse. All images need to be of same shape. Image '{image}' has a different shape than the first image '{images[0]}'.")

def AssembleTimelapse(folder_path, framerate_method, input_framerate, frameselection, inputframes, output_framerate, output_compression, output_format, window, overlay=True, overlayformat='auto', skipframe=1, skip_validation=True):

    if int(output_framerate) > 100 or int(output_framerate) < 1:
        raise Exception(f"{datetime.now().strftime('%H:%M:%S')} ERROR     Choose an output frame rate between 1 and 100.")
    if int(output_compression) > 100 or int(output_compression) < 10:
        raise Exception(f"{datetime.now().strftime('%H:%M:%S')} ERROR     Choose an image compression rate between 10 and 100.")


    now = datetime.now()
    #TODO make variable output_format (avi or mp4).
    video_name = f"{os.path.basename(folder_path)}_PROC{now.strftime('%Y-%m-%d-%H-%M-%S')}.{output_format}"

    outputfile = os.path.join(folder_path, video_name)
    images = [img for img in os.listdir(folder_path) if img.endswith(".tiff") or img.endswith(".png") or img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith(".bmp")]
    if not images:
        raise Exception(f"{datetime.now().strftime('%H:%M:%S')} No images with extension '.tiff', '.png', '.jpg', '.jpeg' or '.bmp' found in selected folder.")
    images = natsorted(images)
    if frameselection == 'All':
        pass
    else:
        try:
            framestart, frameend = inputframes
        except:
            raise Exception(f"{datetime.now().strftime('%H:%M:%S')} ERROR     Give a selection of desired frames: input split by a comma 'start, end' ")
        images = images[framestart:frameend]
    window.Refresh()

    referenceFrame = cv2.imread(os.path.join(folder_path, images[0]))
    (inputHeight, inputWidth, referenceLayers) = referenceFrame.shape

    images_fullpath = [os.path.join(folder_path, i) for i in images]
    deltaTime = get_timestamps(images_fullpath, framerate_method, input_fps=input_framerate)
    timeFromStart = np.cumsum(deltaTime)

    analyze_images = np.arange(0, len(images), skipframe)

    if not skip_validation:
        print(f"{datetime.now().strftime('%H:%M:%S')} Validating images ... This might take a while (depending on the amount of images).")
        window.Refresh()
        window.perform_long_operation(validate_images(analyze_images, images, folder_path, inputHeight, inputWidth, referenceLayers), f"{datetime.now().strftime('%H:%M:%S')} Validation passed successfully.")
        window.Refresh()
    else:
        print(f"{datetime.now().strftime('%H:%M:%S')} Validation of input images is skipped.")


    outputHeight = round(inputHeight * (output_compression / 100))
    outputWidth = round(inputWidth * (output_compression / 100))

    # TODO variable fps!
    video = cv2.VideoWriter(outputfile, 0, output_framerate, (outputWidth, outputHeight))


    fontSizeRatio = 6 / 3000
    ySize = round(180 / 4000 * outputWidth)
    xSize = round(50 / 3000 * outputHeight)
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = outputHeight * fontSizeRatio
    fontColor = (255, 255, 255)
    thickness = round(10 / 4000 * outputWidth)
    lineType = 3

    nowstr = now.strftime('%d-%m-%Y, %H:%M:%S')

    timetracker = []
    for idx in analyze_images:
        imagepath = images[idx]
        start = time.time()  # start timer to calculate iteration time
        img = cv2.imread(os.path.join(folder_path, imagepath))  # load image
        img = cv2.resize(img, (outputWidth, outputHeight), interpolation=cv2.INTER_AREA)

        # Print strings on the image
        # cv2.putText(image, string, location, font, fontscale, fontcolor, fontthickness, linetype)
        if overlay:     #TODO implement overlay ['All', 'time only', 'none'] properly !
            # StringTime = f"t={FancyTimeFormat(idx / input_framerate, len(images) / input_framerate, mode='auto')}"
            StringTime = f"t={FancyTimeFormat(timeFromStart[idx], timeFromStart[-1], mode=overlayformat)}"
            cv2.putText(img, StringTime, (xSize, ySize), font, fontScale, fontColor, thickness, lineType)

            StringPathFolder = textwrap.wrap(f"Original path: {folder_path}", width=100)
            offset = round(fontScale * 10)
            for i, line in enumerate(StringPathFolder):
                # offset = round(i * (fontScale * 10))
                LocationPathFolder = (15 * xSize, round(ySize / 2) + offset * i)
                cv2.putText(img, line, LocationPathFolder, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)

            StringCreatedOn = f"Video created: {nowstr}"
            LocationCreatedOn = (15 * xSize, LocationPathFolder[1] + offset)
            cv2.putText(img, StringCreatedOn, LocationCreatedOn, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)

            StringPathImage = f"{imagepath}"
            LocationPathImage = (xSize, outputHeight - 20)
            cv2.putText(img, StringPathImage, LocationPathImage, font, fontScale * 0.3, fontColor, round(thickness * 0.5), lineType)

            StringImageNumber = f"frame {idx + 1}"
            cv2.putText(img, StringImageNumber, (xSize, ySize * 2), font, fontScale * 0.5, fontColor, round(thickness * 0.5), lineType)

        # Compress image

        video.write(img)  # write frame to file
        timetracker.append(time.time() - start)  # add elapsed time to timetracker array
        TimeRemaining(timetracker, len(analyze_images) - idx/skipframe)  # estimate remaining time based on average time per iteration and iterations left
        window.Refresh()



    cv2.destroyAllWindows()
    video.release()

    print(f"{datetime.now().strftime('%H:%M:%S')} Video saved as {os.path.join(folder_path, outputfile)}.")
    return
