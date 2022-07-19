import PySimpleGUI as sg
import json
from PythonTimelapseAssembler import AssembleTimelapse
from OCA_TiffToVideo import CreateOCAVideo
from datetime import datetime

version = '1.0 (19-07-2022)'

# PyInstaller -F .\TimelapseAssembler.py -n TimelapseAssembler-1_0


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
        sg.Text('Input frame rate'),
        sg.InputText(size=(10, 1), key='fps_input', background_color='white')
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
    [
        sg.Checkbox('Make safe for import OCA (rawvideo)', key='rawvideo', enable_events=True)
    ],
    [
        sg.Checkbox('Overlay video with information (setting does not work yet)', key='overlay')
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
        'rawvideo': window["rawvideo"].get(),
        'overlay': window["overlay"].get(),
    }
    with open('TimelapseAssemblerSettings.json', 'w') as f:
        json.dump(data, f, indent=2)
        print(f"{datetime.now().strftime('%H:%M:%S')} OK        Settings saved as defaults to 'TimelapseAssemblerSettings.json'.")


def SetInitialValues():
    print('----- Simple Timelapse Assembler -----')
    print('by Harmen Hoek')
    print(f"Version: {version}")
    print(f"{datetime.now().strftime('%H:%M:%S')} WARNING   Currently only fixed fps recordings can be processed.")

    try:
        with open('TimelapseAssemblerSettings.json') as f:
            settings = json.load(f)
            window["fps_output"].update(settings['fps_output'])
            window["fps_input"].update(settings['fps_input'])
            window["compression_rate"].update(settings['compression_rate'])
            window["rawvideo"].update(settings['rawvideo'])
            window["overlay"].update(settings['overlay'])
            print(f"{datetime.now().strftime('%H:%M:%S')} OK        Default settings loaded from 'TimelapseAssemblerSettings.json'.")

    except:
        print(f"{datetime.now().strftime('%H:%M:%S')} WARNING   No default settings found. Press 'Set settings as default' to create default settings.")


window = sg.Window("Simple Timelapse Assembler", layout, finalize=True)
SetInitialValues()

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]

    if event == "Create timelapse":
        folder = values["-FOLDER-"]

        if folder:
            print(f"{datetime.now().strftime('%H:%M:%S')} Creating timelapse now ...")
            if values['rawvideo'] == True:
                CreateOCAVideo(folder, int(values["fps_output"]))
            else:
                AssembleTimelapse(folder, int(values["fps_input"]), int(values["fps_output"]), int(values["compression_rate"]))
        else:
            print(f"{datetime.now().strftime('%H:%M:%S')} ERROR     No folder selected.")

    if event == 'Set settings as default':
        SaveAsDefault()

    if values['rawvideo'] == True:
        window['overlay'].update(disabled=True)
        window['compression_rate'].update(disabled=True, text_color='grey')
        window['fps_input'].update(disabled=True, text_color='grey')


    if values['rawvideo'] == False:
        window['overlay'].update(disabled=False)
        window['compression_rate'].update(disabled=False, text_color='black')
        window['fps_input'].update(disabled=False, text_color='black')
