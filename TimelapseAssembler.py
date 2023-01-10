import PySimpleGUI as sg
import json
from PythonTimelapseAssembler import AssembleTimelapse
from OCA_TiffToVideo import CreateOCAVideo
from datetime import datetime
import os
import cv2
import sys
import numpy as np

version = '1.6 (10-10-2023)'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

icon_path = resource_path("timelapse.ico")

# In prompt:
# PyInstaller -F --onefile --noconsole -n TimelapseAssembler-1_3 --icon=timelapse.ico --add-data timelapse.ico;ico .\TimelapseAssembler.py

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
        sg.Text(" ")
    ],
    [
        sg.T('Output settings', font='_ 12 bold', justification='l', expand_x=True),
    ],
    [
        sg.Text('Output frame rate'),
        sg.InputText(size=(10, 1), key='fps_output')
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
        sg.Checkbox('Overlay video with information', key='overlay', enable_events=True)
    ],
    [
        sg.Text("Time format of overlay"),
        sg.Combo(['auto', 'variable', 'ms', 'sec', 'min', 'hrs'], enable_events=True, key='overlayformat', default_value='auto'),
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
        'compression_rate': window["compression_rate"].get(),
        # 'rawvideo': window["rawvideo"].get(),
        'overlay': window["overlay"].get(),
        # 'newHeight': window["newHeight"].get(),
        'inputframerate': window["inputframerate"].get(),
    }
    with open('TimelapseAssemblerSettings.json', 'w') as f:
        json.dump(data, f, indent=2)
        print(f"{datetime.now().strftime('%H:%M:%S')} OK        Settings saved as defaults to 'TimelapseAssemblerSettings.json' (at program location).")


def SetInitialValues():
    print('----- Simple Timelapse Assembler -----')
    print('by Harmen Hoek')
    print(f"Version: {version} (https://github.com/harmenhoek/PythonTimelapseAssembler)")

    try:
        with open('TimelapseAssemblerSettings.json') as f:
            settings = json.load(f)
            window["fps_output"].update(settings['fps_output'])
            window["fps_input"].update(settings['fps_input'])
            window["compression_rate"].update(settings['compression_rate'])
            # window["rawvideo"].update(settings['rawvideo'])
            window["overlay"].update(settings['overlay'])
            # window["newHeight"].update(settings['newHeight'])
            window["inputframerate"].update(settings['inputframerate'])
            window["overlayformat"].update(settings['overlayformat'])
            # if settings['rawvideo'] == True:
            #     window['overlay'].update(disabled=True)
            #     window['compression_rate'].update(disabled=True, text_color='grey')
            #     window['fps_input'].update(disabled=True, text_color='grey')
            #     window['newHeight'].update(disabled=False, text_color='black')
            #     window['calcheight'].update(disabled=False)
            # if settings['rawvideo'] == False:
            #     window['overlay'].update(disabled=False)
            #     window['compression_rate'].update(disabled=False, text_color='black')
            #     window['fps_input'].update(disabled=False, text_color='black')
            #     window['newHeight'].update(disabled=True, text_color='grey')
            #     window['calcheight'].update(disabled=True)
            if settings['inputframerate'] != 'Fixed':
                window['fps_input'].update(disabled=True, text_color='grey')
            if settings['overlay'] == False:
                window['overlayformat'].update(disabled=True, text_color='grey')

            print(f"{datetime.now().strftime('%H:%M:%S')} OK        Default settings loaded from 'TimelapseAssemblerSettings.json'.")

    except:
        print(f"{datetime.now().strftime('%H:%M:%S')} WARNING   No default settings found. Press 'Set settings as default' to create default settings.")



window = sg.Window("Simple Timelapse Assembler", layout, finalize=True, icon=icon_path)
SetInitialValues()

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        files = os.listdir(folder)
        supported_files = [file.endswith((".tiff", ".png", '.jpg', '.jpeg', '.bmp')) for file in files]
        cnt_supported_files = sum(supported_files)
        print(f"{datetime.now().strftime('%H:%M:%S')} Folder {folder} selected, with {cnt_supported_files} supported image files ({len(files)-cnt_supported_files} files ignored).")

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
            AssembleTimelapse(folder, values['inputframerate'], int(values["fps_input"]), int(values["fps_output"]), int(values["compression_rate"]), window, overlay=overlay, overlayformat=values['overlayformat'])

        else:
            print(f"{datetime.now().strftime('%H:%M:%S')} ERROR     No folder selected.")

    if event == 'Set settings as default':
        SaveAsDefault()

    # if event == 'calcheight':
    #     folder = values["-FOLDER-"]
    #     if not folder:
    #         print("Select an image folder first.")
    #     else:
    #         files = os.listdir(folder)
    #         supported_files = [file.endswith((".tiff", ".png", '.jpg', '.jpeg', '.bmp')) for file in files]
    #         cnt_supported_files = sum(supported_files)
    #         newHeight = int(140/cnt_supported_files*1800)  # based on some test results importing into OCA
    #         print(f"Maximum output height is {newHeight} pixels.")
    #         first_image = [file for file, y in zip(files, supported_files) if y == True][0]
    #         if first_image:
    #             first_image_height, w, _ = cv2.imread(os.path.join(folder, first_image)).shape
    #             if newHeight > first_image_height:
    #                 print(f"Maximum output height exceeds original image height ({first_image_height} pixels). Setting output height to {first_image_height} pixels.")
    #                 newHeight = first_image_height
    #             if newHeight > 1800:
    #                 print("Maximum output height exceeds 1800 pixels, thus troublesome to work with in OCA software. Setting output height to 1800 pixels. ")
    #                 newHeight = 1800
    #
    #             window["newHeight"].update(int(newHeight))
    #         else:
    #             print(f"{datetime.now().strftime('%H:%M:%S')}ERROR     No images with extension '.tiff', '.png', '.jpg', '.jpeg' or '.bmp' found in selected folder.")

    if event == 'inputframerate':
        if values['inputframerate'] == 'Fixed':
            window['fps_input'].update(disabled=False, text_color='black')
        else:
            window['fps_input'].update(disabled=True, text_color='grey')

    if event == 'overlay':
        if values['overlay']:
            window['overlayformat'].update(disabled=False)
        else:
            window['overlayformat'].update(disabled=True)


    # if event == 'rawvideo':
    #     if values['rawvideo'] == True:
    #         window['overlay'].update(disabled=True)
    #         window['compression_rate'].update(disabled=True, text_color='grey')
    #         window['fps_input'].update(disabled=True, text_color='grey')
    #         window['newHeight'].update(disabled=False, text_color='black')
    #         window['calcheight'].update(disabled=False)
    #         window['inputframerate'].update(disabled=True, text_color='grey')
    #     if values['rawvideo'] == False:
    #         window['overlay'].update(disabled=False)
    #         window['compression_rate'].update(disabled=False, text_color='black')
    #         window['newHeight'].update(disabled=True, text_color='grey')
    #         window['calcheight'].update(disabled=True)
    #         if window['inputframerate'] == 'Fixed':
    #             window['fps_input'].update(disabled=False, text_color='black')
    #         else:
    #             window['fps_input'].update(disabled=True, text_color='grey')
    #         window['inputframerate'].update(disabled=False, text_color='black')
