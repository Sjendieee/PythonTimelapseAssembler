#import PySimpleGUI as sg    #install an older (non-paid) version: v4.60.3
import FreeSimpleGUI as sg  #a fork from above, since those older packages are removed. https://github.com/spyoungtech/FreeSimpleGUI
import json
from PythonTimelapseAssembler import AssembleTimelapse
from OCA_TiffToVideo import CreateOCAVideo
from datetime import datetime
import os
import cv2
import sys
import numpy as np

version = '1.10 (27-06-2025)'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

icon_path = resource_path("timelapse.ico")

# In prompt:
# PyInstaller -F --onefile --noconsole -n TimelapseAssembler-1_8 --icon=timelapse.ico --add-data timelapse.ico;ico .\TimelapseAssembler.py

#To make .exe executable:                                     _version
# pyinstaller -F --onefile --noconsole -n TimelapseAssembler-1_9 --icon=timelapse.ico --add-data timelapse.ico:ico .\TimelapseAssembler.py


settings_row = [
    [
        sg.T('Settings', font='_ 14', justification='c', expand_x=True),
    ],
    [
        sg.T('Input settings', font='_ 12 bold', justification='l', expand_x=True),
    ],
    [
        sg.Text("Image Folder"),
        sg.In(size=(75, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Input framerate"),
        sg.Combo(['Fixed', 'Read from creation date (Windows only)', 'Read from modified date (Windows only)'], enable_events=True, key='inputframerate', default_value='Fixed'),
    ],
    [
        sg.Text('Input frame rate'),
        sg.InputText(size=(10, 1), key='fps_input', enable_events=True, background_color='white')
    ],

    [
        sg.Text("Input frames"),
        sg.Combo(['All', 'Selection'], enable_events=True, key='inputframes', default_value='All'),
    ],
    [
        sg.Text('Input frame selection'),
        sg.InputText(size=(10, 1), key='frames_input', enable_events=True, background_color='white')
    ],


    [
        sg.Text(" ")
    ],
    [
        sg.T('Output settings', font='_ 12 bold', justification='l', expand_x=True),
    ],
    [
        sg.Text('Output frame rate'),
        sg.InputText(size=(10, 1), key='fps_output', enable_events=True)
    ],
    [
        sg.Text('Compression rate (100=best, 10=worst)'),
        sg.InputText(size=(10, 1), key='compression_rate')
    ],
    # [
    #     sg.Text('Output video height (OCA rawvideo only)'),
    #     sg.InputText(size=(10, 1), key='newHeight', disabled=True),
    #     sg.Button('Calculate max height', enable_events=True, key='calcheight', disabled=False)
    # ],
    # [
    #     sg.Checkbox('Make safe for import OCA (rawvideo)', key='rawvideo', enable_events=True)
    # ],
    [
        sg.Text("Output format"),
        sg.Combo(['avi', 'mp4'], enable_events=True, key='output_format', default_value='mp4')
    ],

    # [
    #     sg.Checkbox('Overlay video with information', key='overlay', enable_events=True, default=True)
    # ],
    [
        sg.Text('Overlay video with information'),
        sg.Combo(['All', 'time only', 'none'], enable_events=True, key='overlay',  default_value='All')
    ],

    [
        sg.Checkbox('Skip image validation', key='skip_validation', enable_events=True, default=False)
    ],
    [
        sg.Text("Time format of overlay"),
        sg.Combo(['auto', 'variable', 'ms', 'sec', 'min', 'hrs'], enable_events=True, key='overlayformat', default_value='auto'),
    ],
    [
        sg.Text('Use every Nth frame'),
        sg.InputText(size=(10, 1), key='skip_frame', default_text='1', enable_events=True)
    ],
]

output_row = [
    [
        sg.T('Output', font='_ 14', justification='c', expand_x=True),
    ],
    [
        sg.Output(s=(100, 15), key='outputbox'),
    ],
]



# ----- Full layout -----
layout = [
    [
        settings_row,
    ],
    [
        sg.HSeparator(),
    ],
    [
        output_row,
    ],
    [
        sg.Button('Create timelapse'),
        sg.Push(),
        sg.Button('Set settings as default'),
        sg.Button('Exit'),
    ],
]


def SaveAsDefault():
    data = {
        'fps_output': window["fps_output"].get(),
        'fps_input': window["fps_input"].get(),
        'frames_input': window["frames_input"].get(),
        'compression_rate': window["compression_rate"].get(),
        'output_format': window["output_format"].get(),
        'overlay': window["overlay"].get(),
        'skip_validation': window["skip_validation"].get(),
        'inputframerate': window["inputframerate"].get(),
        'inputframes': window["inputframes"].get(),
        'skip_frame': window["skip_frame"].get(),
    }
    with open('TimelapseAssemblerSettings.json', 'w') as f:
        json.dump(data, f, indent=2)
        print(f"{datetime.now().strftime('%H:%M:%S')} OK        Settings saved as defaults to 'TimelapseAssemblerSettings.json' (at program location).")


def SetInitialValues():
    print('----- Simple Timelapse Assembler -----')
    print('by Harmen Hoek & Sander Reuvekamp')
    print(f"Version: {1.8} (https://github.com/harmenhoek/PythonTimelapseAssembler)")
    print(f"Version: {version} (https://github.com/Sjendieee/PythonTimelapseAssembler)")

    try:
        with open('TimelapseAssemblerSettings.json') as f:
            settings = json.load(f)
            window["fps_output"].update(settings['fps_output'])
            window["fps_input"].update(settings['fps_input'])
            window["frames_input"].update(settings['frames_input'])
            window["compression_rate"].update(settings['compression_rate'])
            window["output_format"].update(settings['output_format'])
            window["overlay"].update(settings['overlay'])
            window["skip_validation"].update(settings['skip_validation'])
            window["inputframerate"].update(settings['inputframerate'])
            window["inputframes"].update(settings['inputframes'])
            window["skip_frame"].update(settings['skip_frame'])

            # set initial disabled buttons
            if settings['fps_input'] != 'Fixed':
                window['fps_input'].update(disabled=False, text_color='black')
            if settings['frames_input'] == 'All':
                window['frames_input'].update(disabled=True, text_color='grey')
            if settings['overlay'] == False:
                window['overlayformat'].update(disabled=True, text_color='grey')


            print(f"{datetime.now().strftime('%H:%M:%S')} OK        Default settings loaded from 'TimelapseAssemblerSettings.json'.")

    except:
        print(f"{datetime.now().strftime('%H:%M:%S')} WARNING   No default settings found. Press 'Set settings as default' to create default settings.")
        # set initial disabled buttons if no default settings are available
        window['fps_input'].update(disabled=False, text_color='black')
        window['frames_input'].update(disabled=True, text_color='grey')
        window['overlayformat'].update(disabled=False)
        window['overlay'].update(disabled=False)
        window['inputframerate'].update('Fixed')
        window['inputframes'].update('All')



def cnt_images_in_folder(folder):
    files = os.listdir(folder)
    cnt_files = len(files)
    supported_files = [file.endswith((".tiff", ".png", '.jpg', '.jpeg', '.bmp')) for file in files]
    cnt_supported_files = sum(supported_files)
    cnt_images_analyzed = round(cnt_supported_files / int(values['skip_frame']))
    return cnt_files, cnt_supported_files, cnt_images_analyzed

window = sg.Window("Simple Timelapse Assembler", layout, finalize=True, icon=icon_path)
SetInitialValues()

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        cnt_files, cnt_supported_files, cnt_images_analyzed = cnt_images_in_folder(folder)
        if values['fps_output']:
            extra_str = f" (about {round(cnt_images_analyzed / int(values['fps_output']))} seconds)"
        else:
            extra_str = ''
        print(f"{datetime.now().strftime('%H:%M:%S')} Folder {folder} selected, with {cnt_supported_files} supported image files ({cnt_files-cnt_supported_files} files ignored). {cnt_images_analyzed} used for movie{extra_str}.")

    if event == 'skip_frame' and values["-FOLDER-"]:
        if values['skip_frame']:
            folder = values["-FOLDER-"]
            cnt_files, cnt_supported_files, cnt_images_analyzed = cnt_images_in_folder(folder)
            if values['fps_output']:
                extra_str = f" (about {round(cnt_images_analyzed / int(values['fps_output']))} seconds)"
            else:
                extra_str = ''
            print(f"{datetime.now().strftime('%H:%M:%S')} {cnt_supported_files} images in total, movie will consist of {cnt_images_analyzed} images{extra_str}.")

    if event == 'fps_output' and values["-FOLDER-"]:
        folder = values["-FOLDER-"]
        cnt_files, cnt_supported_files, cnt_images_analyzed = cnt_images_in_folder(folder)
        extra_str = f" (final video about {round(cnt_images_analyzed / int(values['fps_output']))} seconds)"
        print(f"{datetime.now().strftime('%H:%M:%S')} {cnt_supported_files} images in total, movie will consist of {cnt_images_analyzed} images{extra_str}.")


    if event == "Create timelapse":
        folder = values["-FOLDER-"]

        if folder:
            print(f"{datetime.now().strftime('%H:%M:%S')} Creating timelapse now ...")

            # if values['rawvideo'] == True:
            #     CreateOCAVideo(folder, int(values["fps_output"]), int(values["newHeight"]))
            # else:
            #     overlay = values['overlay']
            #     AssembleTimelapse(folder, values['inputframerate'], int(values["fps_input"]), int(values["fps_output"]), int(values["compression_rate"]), window, overlay=overlay, overlayformat=values['overlayformat'])
            overlay = values['overlay']
            skip_frame = int(values['skip_frame'])
            fps_input = int(values["fps_input"]) if values["fps_input"] else 0

            try:
                if values["frames_input"]:
                    framestart, frameend = values["frames_input"].split(',')
                    if framestart < 0 or frameend > cnt_supported_files:
                        raise Exception( f"{datetime.now().strftime('%H:%M:%S')} ERROR     Selection reaches outside possible range (0< or >{cnt_supported_files}: nr of supported files)")
                    frames_input = [int(framestart), int(frameend)]
                else:
                    frames_input = 0
            except:
                raise Exception(f"{datetime.now().strftime('%H:%M:%S')} ERROR     Give a selection of desired frames: input split by a comma 'start, end' ")

            AssembleTimelapse(folder, values['inputframerate'], fps_input, values['inputframes'], frames_input,
                              int(values["fps_output"]), int(values["compression_rate"]), values["output_format"], window, overlay=overlay, overlayformat=values['overlayformat'], skipframe=skip_frame, skip_validation=values['skip_validation'])

        else:
            print(f"{datetime.now().strftime('%H:%M:%S')} ERROR     No folder selected.")

    if event == 'Set settings as default':
        SaveAsDefault()

    if event == 'inputframerate':
        if values['inputframerate'] == 'Fixed':
            window['fps_input'].update(disabled=False, text_color='black')
        else:
            window['fps_input'].update(disabled=True, text_color='grey')

    if event == 'inputframes':
        if values['inputframes'] == 'All':
            window['frames_input'].update(disabled=True, text_color='grey')
        else:
            window['frames_input'].update(disabled=False, text_color='black')

    if event == 'overlay':
        if values['overlay']:
            window['overlayformat'].update(disabled=False)
        else:
            window['overlayformat'].update(disabled=True)

