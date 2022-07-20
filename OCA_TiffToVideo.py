import os
import ffmpeg
from datetime import datetime

'''
This program converts a bunch of images into a video format that can be imported on the Dataphysics OCA 15plus.

Input: folder with images (tiff, png, jpg, jpeg, bmp)
Output: video file (codec:rawvideo)

NOTE To run this code:
1. install FFmpeg locally with correct enviromental variables! https://www.wikihow.com/Install-FFmpeg-on-Windows
2. install requirements (ffmpeg-python, tk)

Special thanks to Harro Beens for figuring out the correct format, codec and scaling.

July 2022 - Physics of Complex Fluids
'''

def CreateOCAVideo(folder_path, output_fps, newHeight):

    print('----- Image to video converter for Dataphysics OCA 15plus -----')
    print('Special thanks to Harro Beens for figuring out the correct codec.')
    print(f"{datetime.now().strftime('%H:%M:%S')} Creating video (this might take a while)...")

    now = datetime.now()

    filenameExport = f"{os.path.basename(os.path.normpath(folder_path))}_PROC{now.strftime('%Y-%m-%d-%H-%M-%S')}.avi"

    images = [os.path.join(folder_path, img) for img in os.listdir(folder_path) if
              img.endswith(".tiff") or img.endswith(".png") or img.endswith(".jpg") or img.endswith(
                  ".jpeg") or img.endswith(".bmp")]
    if not images:
        raise Exception(f"{datetime.now().strftime('%H:%M:%S')} No images with extension '.tiff', '.png', '.jpg', '.jpeg' or '.bmp' found in selected folder.")

    with open('temp.txt', 'w') as f:
        for image in images:
            f.write(f"file '{image}'\n")

    try:
        _, _ = (
            ffmpeg
                .input('temp.txt', r=output_fps, f='concat', safe='0')
                .output(filenameExport, vf=f'scale={newHeight}:-1', vcodec='rawvideo', crf=0)
                .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        print(f"{datetime.now().strftime('%H:%M:%S')}  {e.stderr}")
        print(f"{datetime.now().strftime('%H:%M:%S')} Do you have ffmpeg installed on your computer? https://www.wikihow.com/Install-FFmpeg-on-Windows")

    os.remove('temp.txt')
    print(f"{datetime.now().strftime('%H:%M:%S')} Video {filenameExport} created successfully!")
    print(f"{datetime.now().strftime('%H:%M:%S')} 'Note: VLC does not play rawvideo.")
