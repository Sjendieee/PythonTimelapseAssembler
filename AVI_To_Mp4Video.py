import os
from pathlib import Path
import ffmpeg           #ffmpeg-python proberen zodat de .exe niet nodig is?

# ffmpeg -i D:\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_____BAD\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_PROC2023-03-20-10-34-11.avi -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 output.mp4


def convert_avi_to_mp4(avi_file_path):
    output_name = os.path.join(os.path.dirname(avi_file_path), Path(avi_file_path).stem)
    #os.popen("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'".format(input = avi_file_path, output = output_name))
    print(f"1 we get here")
    input = avi_file_path
    output = output_name
    print(f"{output_name}")
    #Working version, difficult because of externally downloaded ffmpeg.exe executable:
    #os.popen(os.path.join(f".\\venv\\ffmpeg\\ffmpeg.exe  -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}.mp4"))
    os.popen(os.path.join(f"ffmpeg -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}.mp4"))

    print(f"2 we get here")
    return True

#TODO trying ffmpeg-ython package, to make this entire file into an executable
def convert_avi_to_mp4_v2(avi_file_path):
    output_name = os.path.join(os.path.dirname(avi_file_path), Path(avi_file_path).stem)
    print(f"1 we get here")
    input = avi_file_path
    output = os.path.join(f"{output_name}.mp4")
    print(f"Making mp4 file in: {output}")
    #Working version, difficult because of externally downloaded ffmpeg.exe executable (needs full version to work?):
    #os.popen(os.path.join(f".\\venv\\ffmpeg\\ffmpeg.exe  -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}.mp4"))
    (
        ffmpeg
        .input(input)
        .output(output, **{'ac': 2,                    #
                                'b:v': '2000k',             # video bitrate constant
                                'c:a': 'aac',               # codec audio
                                'c:v': 'libx264',           # codec video
                                'b:a': '160k',              # audio bitrate constant
                                'vprofile': 'high',         #
                                'bf': 0,                    #
                                'strict': 'experimental',   #
                                'f': 'mp4'})                # format=mp4
     )
    #os.popen(os.path.join(f"ffmpeg -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}.mp4"))

    print(f"2 we get here")
    return True

def main():
    path = "D:\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_____BAD\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_PROC2023-03-20-10-34-11.avi"
    convert_avi_to_mp4_v2(path)

#Dit werkte in terminal:
#.\venv\ffmpeg\ffmpeg.exe -i D:\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_____BAD\\2023_03_16_PLMA_Tetradecane_Basler2x_Xp1_24_S11_split_PROC2023-03-20-10-34-11.avi -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 output.mp4


if __name__ == "__main__":
    main()