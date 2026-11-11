# Simple Timelapse Assembler

**Version 1_11_4** · Windows GUI for converting image sequences into timelapse videos, with optional elapsed-time, experiment metadata, and temperature overlays.

Originally developed for experimental image sequences, **Simple Timelapse Assembler** turns a folder of images into an `.mp4` or `.avi` movie. It is particularly useful when a recording needs to show the physical experiment time rather than just the video playback time.

The application is written in Python and can be run as a standalone Windows executable or directly from the source code.

## Features

- **Image-to-video conversion** for `.tiff`, `.png`, `.jpg`, `.jpeg`, and `.bmp` images.
- **MP4 or AVI output**, with adjustable playback frame rate and output resolution.
- **Natural filename sorting** (`frame2.png` comes before `frame10.png`).
- **Experimental time overlays** calculated from either a fixed interval or Windows file timestamps.
- **Three overlay modes:** elapsed time plus metadata, elapsed time only, or no overlay.
- **Configurable time display** in milliseconds, seconds, minutes, hours, or an automatically chosen format.
- **Temperature annotations** assigned to user-defined frame ranges.
- **Frame-range selection** and optional temporal subsampling (use every *N*th image).
- **Optional image-size validation** before processing.
- **Processing messages and estimated remaining time** in the application window.
- **Reusable default settings**, stored in a local JSON file.

> **Scope:** The current GUI produces videos at a **constant output frame rate**, even when file timestamps are used for the displayed experimental time. The legacy DataPhysics OCA rawvideo exporter is present in a separate Python module, but it is **not currently selectable from the GUI**. The standard `.avi` output uses XVID instead.

## Quick start (Windows executable)

1. Open the [`dist` directory](https://github.com/Sjendieee/PythonTimelapseAssembler/tree/main/dist) and obtain the appropriate `TimelapseAssembler*.exe` file.
2. Run the executable; no separate Python installation is needed for a correctly packaged build.
3. Under **Image Folder**, select the folder containing the image sequence.
4. Choose how the experiment time should be determined under **Input framerate** (see [Input timing](#input-timing)).
5. Set the **Output frame rate** (for example, `15`), **Compression rate** (for example, `20`), and **Output format** (`mp4` recommended for general playback).
6. Select the desired overlay mode and, optionally, add temperature annotations or select/skip frames.
7. Click **Create timelapse**. Processing status appears in the **Output** panel.

The movie is saved **in the selected image folder** and named approximately:

```text
<image-folder-name>_PROC2026-11-11-16-30-00.mp4
```

The application holds the final processed frame for approximately **one additional second**.

## Settings reference

### Input settings

| GUI setting | Description |
| --- | --- |
| **Image Folder** | Folder containing the images. Images are read from this folder, not recursively from its subfolders. |
| **Input framerate** | Determines how experimental time is calculated: `Fixed`, `Read from creation date (Windows only)`, or `Read from modified date (Windows only)`. |
| **Input frame rate** | Numeric interval used in `Fixed` mode for the time overlay. **Despite the GUI label, the current implementation treats this value as seconds per input image, not frames per second.** Use `1` for images acquired one second apart, `10` for images acquired ten seconds apart, etc. The GUI currently parses this field as an integer when processing starts. |
| **Input frames** | `All` for the entire sequence, or `Selection` to process a specific portion. |
| **Input frame selection** | For `Selection`, enter `start,end` (for example, `100,500`). The Python implementation uses **zero-based indices**, with the start **included** and the end **excluded**, so this example takes 400 images before skipping. |

### Output settings

| GUI setting | Description |
| --- | --- |
| **Output frame rate** | Playback rate of the created video, **1–100 fps**. Higher values make a given number of frames play faster. |
| **Compression rate** | **10–100**, interpreted as a percentage of the original image **width and height**. `100` preserves the original dimensions; `50` halves both dimensions (one quarter of the pixels). This is **spatial downscaling**, not an encoder-quality or bitrate control. |
| **Output format** | `mp4` (OpenCV MPEG-4 / `mp4v`) or `avi` (OpenCV XVID). |
| **Overlay video with information** | `Time+meta`, `Time`, or `None`. See [Overlays](#overlays). |
| **Add temperature overlay** | Opens the frame-range editor for temperature annotations. |
| **Skip image validation** | Disables the pre-processing check that selected images have matching dimensions and can be read. Useful for speed when the source images are known to be consistent. |
| **Time format of overlay** | `full`, `variable`, `ms`, `sec`, `min`, or `hrs`. |
| **Use every Nth frame** | `1` uses every image; `2` uses every second image; `10` uses every tenth image, starting from the beginning of the selected range. Use an integer of at least `1`. |

### Example: choosing video speed

Suppose a folder contains **900 images** taken at **one-second intervals**:

| Setting | Value |
| --- | --- |
| Input framerate | `Fixed` |
| Input frame rate | `1` (one second per image) |
| Output frame rate | `30` fps |
| Use every Nth frame | `1` |
| Compression rate | `100` |
| Output format | `mp4` |
| Overlay | `Time` |

The experiment spans roughly **15 minutes**. Its 900 images produce about **30 seconds of moving video**, plus the one-second hold on the final image. The visible `t=...` overlay follows the experiment timeline rather than the compressed playback timeline.

For the same input, `Use every Nth frame = 5` reduces the moving part to around **6 seconds** at 30 fps while retaining the experimental-time values for the frames that are actually shown.

## Input timing

The program distinguishes between **experimental time** (shown in an overlay) and **video playback speed** (controlled by output fps).

- **Fixed:** each successive source image is assigned the interval specified in **Input frame rate**, in seconds. For example, enter `5` if the images were acquired every five seconds. **Current implementation detail:** the first image is labeled at one interval (`t=5s` in this example), rather than `t=0`.
- **Read from creation date (Windows only):** experimental time is calculated from the files' creation timestamps. The first image starts at `t=0`.
- **Read from modified date (Windows only):** experimental time is calculated from last-modified timestamps. The first image starts at `t=0`.

The images are **ordered by naturally sorted filenames**, not by their timestamps. If timestamps are used, keep the filenames consistent with the actual acquisition order. Copying, transferring, or editing image files may change their filesystem timestamps; the creation time in particular may reflect when a file was copied rather than when the image was recorded.

**Important:** Timestamp-based timing affects the **overlay only**. The exported video still has a constant output fps; frames are not held for different durations to reproduce irregular acquisition intervals.

## Overlays

### Overlay modes

| Mode | Information shown on the video |
| --- | --- |
| **Time+meta** | Experimental elapsed time, frame number, source filename, original folder path, and video creation date/time. Also shows a matching temperature annotation if configured. |
| **Time** | Experimental elapsed time, plus any configured temperature annotation. |
| **None** | No text annotations, including no temperature annotation. |

**Privacy note:** `Time+meta` writes the source folder path directly into the video. Select `Time` if you plan to publish or share a video without exposing local directory names.

### Time formatting

| Option | Behavior |
| --- | --- |
| `full` | Shows an automatically appropriate time format; for longer experiments this can include multiple units (for example minutes and seconds). |
| `variable` | Uses a compact single-unit presentation, depending on elapsed time. |
| `ms` | Always displays rounded milliseconds. |
| `sec` | Always displays rounded seconds. |
| `min` | Always displays rounded minutes. |
| `hrs` | Always displays rounded hours. |

### Temperature annotations

Click **Add temperature overlay** to assign temperatures to frame ranges. For example:

| Frame start | Frame end | Temperature |
| --- | --- | --- |
| `0` | `149` | `25` °C |
| `150` | `299` | `40` °C |
| `300` | `449` | `60` °C |

Use **Add** to create an entry, **Remove selected** to delete one, and **OK** to apply the entries to the current session. Each frame range includes both its start and end value. When multiple entries overlap, the first matching entry in the list takes precedence.

Temperatures appear as `T=25.0 C` beneath the time annotation. A frame outside the defined ranges has no temperature label. To display temperatures, select either `Time` or `Time+meta`; they are not displayed when the overall overlay mode is `None`.

> **Frame selection caveat:** The current implementation handles temperature range indices differently when a subset of frames is selected. For reliable frame-to-temperature correspondence, prefer `Input frames = All` when using temperature annotations, and check the exported movie carefully if combining annotations with a frame selection. Temperature entries are **not** stored by **Set settings as default**.

## Frame selection and subsampling

Frames are processed in their **natural filename order**. If you want only images 100 through 499 (400 images), use:

```text
Input frames:           Selection
Input frame selection:  100,500
Use every Nth frame:    1
```

To process every fifth image from that selection:

```text
Input frames:           Selection
Input frame selection:  100,500
Use every Nth frame:    5
```

This results in **80 video frames**, before the final-frame hold. The application applies the selection first and the *N*th-frame sampling afterward.

The frame count and predicted duration displayed in the GUI are **approximate**; in the current source they may not fully account for a selected range or for the additional final-frame hold.

## Saving default settings

Click **Set settings as default** to create or update:

```text
TimelapseAssemblerSettings.json
```

The file is read when the application starts again. It stores frame-rate settings, frame selection, output format, output scale, overlays, time format, validation choice, and frame-skipping settings.

The selected image folder and temperature annotation ranges are **not saved**. The JSON is written relative to the application's **current working directory**, which is usually the executable's directory when launched directly, but can differ when started from a terminal or shortcut.

## Running from Python source

For development, the entry point is [`TimelapseAssembler.py`](TimelapseAssembler.py); the video-generation logic is in [`PythonTimelapseAssembler.py`](PythonTimelapseAssembler.py).

From the repository directory, install the required packages in your Python environment:

```powershell
python -m pip install FreeSimpleGUI opencv-python numpy natsort ffmpeg-python
```

Then start the GUI:

```powershell
python TimelapseAssembler.py
```

`tkinter` is part of standard Windows Python installations. The `ffmpeg-python` package is needed for the import of the legacy OCA module, but the **currently active MP4/AVI GUI workflow uses OpenCV** and does not need a separately installed FFmpeg executable.

### Building the Windows executable

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Run this command from the repository root:

```powershell
pyinstaller --onefile --noconsole --name "TimelapseAssembler-1_11_4" --icon "TimelapseIcon_new.ico" --add-data "TimelapseIcon_new.ico;." TimelapseAssembler.py
```

The executable is created in `dist/`. The icon is bundled at the root of PyInstaller's resource directory, where the code expects to find it. Make sure the GUI's `version` string matches the release you are building.

**Note:** The OCA-specific `OCA_TiffToVideo.py` and AVI conversion utility are retained as source modules, but their legacy workflows are not currently accessible as separate options in the GUI. They should not be confused with the normal AVI output.

## Troubleshooting and limitations

| Issue | Suggested check |
| --- | --- |
| **No images detected** | The current extension filter matches lowercase `.tiff`, `.png`, `.jpg`, `.jpeg`, and `.bmp`. It does **not** include `.tif` or uppercase extensions such as `.JPG`. |
| **Images rejected during validation** | Ensure files are readable and have matching dimensions. Only use **Skip image validation** if you understand and accept the risk of inconsistent inputs. |
| **Incorrect elapsed times** | Check whether you chose a fixed interval or filesystem timestamps. Remember that the GUI's fixed input field is treated as **seconds per image**, not true input fps. |
| **Wrong image order** | Rename images into a consistent sequence; the code uses natural filename sorting rather than timestamp sorting. |
| **Unexpectedly short or long output** | Check **Output frame rate**, **Use every Nth frame**, and any frame selection. Duration is approximately `(written frames / output fps) + 1 second`. |
| **Very small output video** | **Compression rate** changes output width *and* height. Try `100` first. |
| **Temperature label missing** | Check that the frame lies inside one of the entered ranges and that the overlay mode is not `None`. |
| **AVI cannot be imported by OCA software** | The regular GUI AVI uses **XVID**, not the OCA-specific rawvideo codec. The legacy OCA export is not currently exposed in the GUI. |
| **Executable is blocked by Windows** | Verify that the file came from the intended repository and that you trust it. Check Windows security notifications and the file's **Properties** for an applicable **Unblock** option rather than disabling security protections. |

Other current limitations: output is constant-frame-rate, the video has no audio, and the GUI does not provide batch processing across multiple input folders.

## Project files

| File or directory | Purpose |
| --- | --- |
| [`TimelapseAssembler.py`](TimelapseAssembler.py) | Main GUI and settings management; application entry point. |
| [`PythonTimelapseAssembler.py`](PythonTimelapseAssembler.py) | Image sorting, timing, overlays, validation, and video assembly. |
| [`OCA_TiffToVideo.py`](OCA_TiffToVideo.py) | Legacy DataPhysics OCA rawvideo exporter (not currently invoked by the GUI). |
| [`AVI_To_Mp4Video.py`](AVI_To_Mp4Video.py) | Separate experimental AVI-to-MP4 conversion utility. |
| [`dist/`](dist/) | Packaged executable builds. |
| [`screenshots/`](screenshots/) | Screenshots included in the repository. |

## Credits

Developed by **Harmen Hoek** and **Sander Reuvekamp**, originally for scientific timelapse processing and experimental data visualization.

For bugs, questions, or improvements, see the [GitHub repository](https://github.com/Sjendieee/PythonTimelapseAssembler) and its [Issues page](https://github.com/Sjendieee/PythonTimelapseAssembler/issues).
