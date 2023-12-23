import os
import subprocess
import random
from pathlib import Path
from datetime import datetime, timedelta

def get_next_monday_month(current_date):
    days_until_next_monday = (7 - current_date.weekday()) % 7
    next_monday = current_date + timedelta(days=days_until_next_monday)
    return next_monday.strftime("%m")

def get_week_number(current_date):
    days_until_next_monday = (7 - current_date.weekday()) % 7
    next_monday = current_date + timedelta(days=days_until_next_monday)
    week_of_month = (next_monday.day - 1) // 7 + 1
    return f"{week_of_month:02d}"

def get_timecode_arg(input_file):
    timecode = (
        subprocess.check_output(
            ["mediainfo", "--Inform=Video;%TimeCode_FirstFrame%", input_file]
        )
        .decode()
        .strip()
    )
    return f"-timecode {timecode}" if timecode else ""

def process_file(input_file, youtubefolder, salemfolder, captions):
    src_folder = os.path.dirname(input_file)
    file = os.path.basename(input_file)

    timecode_arg = get_timecode_arg(input_file)

    def generate_output_path(base_folder, ext):
        base_name = os.path.splitext(file)[0]
        return os.path.join(base_folder, f"{base_name}.{ext}")

    ytmov = generate_output_path(youtubefolder, "mov")
    ytmp4 = generate_output_path(youtubefolder, "mp4")
    ytmp4cc = generate_output_path(youtubefolder, "cc.mp4")
    slmov = generate_output_path(salemfolder, "mov")
    slmp4 = generate_output_path(salemfolder, "mp4")
    slmp4cc = generate_output_path(salemfolder, "cc.mp4")

    if captions:
        if os.path.exists(ytmp4):
            for output_file in [ytmov, slmov]:
                subprocess.run([
                    "ffmpeg", "-i", output_file, "-hide_banner", "-map", "0:v", "-map", "0:a", timecode_arg, "-c", "copy", output_file
                ])

        else:
            ffmpeg_cmd = [
                "ffmpeg",
                "-i",
                input_file,
                "-map",
                "0:v",
                "-map",
                "0:a?",
                "-hide_banner",
                "-b:a",
                "320k",
                "-metadata",
                "xmp=",
                "-vf",
                "yadif=1:0",
                "-y",
                "-pix_fmt",
                "yuv420p",
                "-loglevel",
                "verbose",
                "-g",
                "180",
                "-maxrate:v",
                "20M",
                "-bufsize:v",
                "20M",
                "-aspect",
                "16:9",
                "-c:v",
                "libx264",
                "-crf",
                "16",
                "-x264opts",
                "ref=4:qpmin=4:colorprim=bt709:transfer=bt709:colormatrix=bt709",
                "-preset:v",
                "fast",
                timecode_arg,
                ytmov,
                "-b:a",
                "128K",
                "-metadata",
                "xmp=",
                "-vf",
                "yadif=0:0,scale=1280:720",
                "-y",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "29.97",
                "-loglevel",
                "verbose",
                "-g",
                "180",
                "-maxrate:v",
                "10M",
                "-bufsize:v",
                "10M",
                "-aspect",
                "16:9",
                "-c:v",
                "libx264",
                "-crf",
                "25",
                "-x264opts",
                "ref=4:qpmin=4:colorprim=bt709:transfer=bt709:colormatrix=bt709",
                timecode_arg,
                slmov,
                "-vn",
                "-ar",
                "44100",
                "-b:a",
                "96k",
                "-metadata:s:a:0",
                "language=eng",
                "-y",
                os.path.join(salemfolder, "mp3", f"{os.path.splitext(file)[0]}.mp3"),
            ]
            subprocess.run(ffmpeg_cmd)

        captions_line = subprocess.check_output(["sed", "-n", "5p", captions]).decode().strip()
        Isdp = "df" if captions_line[8] == ";" else "ndf"

        command1 = f"-tcmode=29.97{Isdp}"
        command2 = f"-command=changetcmode,59.94{Isdp}"

        def run_mac_caption(movie_file, target_file):
            mac_caption_args = [
                "/Applications/MacCaption.app/Contents/MacOS/MacCaption",
                "-omit_reading_preferences_file",
                "-movie",
                movie_file,
                command1,
                "-import=scc",
                "-displaymode=caption",
                "-ioptions=A1",
                "-input",
                captions,
                command2,
                "-addtofile=quicktime608",
                "-addtofile_target",
                target_file,
            ]

            subprocess.run(mac_caption_args)

        run_mac_caption(ytmov, ytmov)
        run_mac_caption(slmov, slmov)

        def run_mp4box(movie_file, output_file):
            mp4box_args = [
                "/Applications/GPAC.app/Contents/MacOS/MP4Box",
                "-add",
                movie_file,
                "-lang",
                "1=Eng",
                "-lang",
                "2=eng",
                "-lang",
                "3=eng",
                "-lang",
                "4=eng",
                "-new",
                output_file,
            ]

            subprocess.run(mp4box_args)

        run_mp4box(ytmov, ytmp4cc)
        run_mp4box(slmov, slmp4cc)

        captions_txt = f"{os.path.splitext(captions)[0]}.txt"
        if not os.path.exists(captions_txt):
            mac_caption_args = [
                "/Applications/MacCaption.app/Contents/MacOS/MacCaption",
                "-import=scc",
                "-displaymode=caption",
                "-ioptions=A1",
                "-input",
                captions,
                "-export=plaintext",
                "-output",
                captions_txt,
            ]

            subprocess.run(mac_caption_args)

        transcripts_folder = os.path.join(salemfolder, "Transcripts")
        os.makedirs(transcripts_folder, exist_ok=True)

        subprocess.run(["txt2pdf", captions_txt, os.path.join(transcripts_folder, f"{os.path.splitext(file)[0]}.pdf")])

        if os.path.exists(ytmp4):
            uncaptioned_folder = os.path.join(youtubefolder, "uncaptioned")
            os.makedirs(uncaptioned_folder, exist_ok=True)
            os.rename(ytmp4, os.path.join(uncaptioned_folder, f"{os.path.basename(ytmp4)}"))

        if os.path.exists(slmp4):
            uncaptioned_folder = os.path.join(salemfolder, "uncaptioned")
            os.makedirs(uncaptioned_folder, exist_ok=True)
            os.rename(slmp4, os.path.join(uncaptioned_folder, f"{os.path.basename(slmp4)}"))

    else:
        if not os.path.exists(ytmp4):
            ffmpeg_cmd = [
                "ffmpeg",
                "-i",
                input_file,
                "-map",
                "0:v",
                "-map",
                "0:a?",
                "-b:a",
                "320k",
                "-metadata",
                "xmp=",
                "-vf",
                "yadif=1:0",
                "-pix_fmt",
                "yuv420p",
                "-g",
                "180",
                "-maxrate:v",
                "20M",
                "-bufsize:v",
                "20M",
                "-aspect",
                "16:9",
                "-c:v",
                "libx264",
                "-crf",
                "16",
                "-x264opts",
                "ref=4:qpmin=4:colorprim=bt709:transfer=bt709:colormatrix=bt709",
                "-movflags",
                "+faststart",
                timecode_arg,
                ytmp4,
                "-b:a",
                "128K",
                "-metadata",
                "xmp=",
                "-vf",
                "yadif=0:0,scale=1280:720",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "29.97",
                "-g",
                "180",
                "-maxrate:v",
                "10M",
                "-bufsize:v",
                "10M",
                "-aspect",
                "16:9",
                "-c:v",
                "libx264",
                "-crf",
                "25",
                "-x264opts",
                "ref=4:qpmin=4:colorprim=bt709:transfer=bt709:colormatrix=bt709",
                "-movflags",
                "+faststart",
                timecode_arg,
                slmp4,
                "-vn",
                "-ar",
                "44100",
                "-b:a",
                "96k",
                "-metadata:s:a:0",
                "language=eng",
                "-y",
                os.path.join(salemfolder, "mp3", f"{os.path.splitext(file)[0]}.mp3"),
            ]

            subprocess.run(ffmpeg_cmd)

        duration = (
            int(subprocess.check_output(["mediainfo", "--Inform=General;%Duration%", input_file].decode()).strip())
            / 1000
        ) - 120

        scan_type = subprocess.check_output(["mediainfo", "--Inform=Video;%ScanType%", input_file]).decode().strip()
        if scan_type != "Progressive":
            print("Video isn't Progressive... Will De-Iterlace Thumbnail.")
            for n in range(1, 31):
                rand = random.randint(60, int(duration) + 60)
                subprocess.run([
                    "ffmpeg", "-ss", str(rand), "-i", input_file, "-vf", "bwdif", "-frames:v", "1", "-y",
                    os.path.join(youtubefolder, "thumbs", f"{os.path.splitext(file)[0]}-{rand}.jpg")
                ])
                subprocess.run([
                    "ffmpeg", "-ss", str(rand), "-i", input_file, "-vf", "bwdif,scale=852:480", "-frames:v", "1", "-y",
                    os.path.join(salemfolder, "thumbs", f"{os.path.splitext(file)[0]}-{rand}.jpg")
                ])
        else:
            print("Video is Progressive!!! Yay!")
            for n in range(1, 31):
                rand = random.randint(60, int(duration) + 60)
                subprocess.run([
                    "ffmpeg", "-ss", str(rand), "-i", input_file, "-frames:v", "1", "-y",
                    os.path.join(youtubefolder, "thumbs", f"{os.path.splitext(file)[0]}-{rand}.jpg")
                ])
                subprocess.run([
                    "ffmpeg", "-ss", str(rand), "-i", input_file, "-frames:v", "1", "-vf", "scale=852:480", "-y",
                    os.path.join(salemfolder, "thumbs", f"{os.path.splitext(file)[0]}-{rand}.jpg")
                ])

def main():
    today = datetime.now()
    month = get_next_monday_month(today)
    weeknum = get_week_number(today)
    week = f"{month}-{weeknum}"

    nextweekfolder = os.path.realpath(f"/Volumes/Storage/PIJN/{week}")

    if not Path(nextweekfolder).is_dir():
        print("Next week's folder does not exist.")
        return

    for root, _, files in os.walk(nextweekfolder):
        for file in files:
            if file.endswith(".mpg"):
                input_file = os.path.join(root, file)
                process_file(input_file, f"{root}/youtube", f"{root}/salem", "")

if __name__ == "__main__":
    main()
