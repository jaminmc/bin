import os
import subprocess
import random
from pathlib import Path
from datetime import datetime
from datetime import timedelta

today = datetime.now()


def get_next_monday_month():
    days_until_next_monday = (7 - today.weekday()) % 7
    next_mon = today + timedelta(days=days_until_next_monday)
    month_number = next_mon.strftime("%m")
    return month_number


def get_week_number():
    days_until_next_monday = (7 - today.weekday()) % 7
    next_mon = today + timedelta(days=days_until_next_monday)
    week_of_month = (next_mon.day - 1) // 7 + 1
    weeknum = f"{week_of_month:02d}"
    return weeknum


def process_file(input_file, youtubefolder, salemfolder, captions):
    src_folder = os.path.dirname(input_file)
    file = os.path.basename(input_file)

    timecode = (
        subprocess.check_output(
            ["mediainfo", "--Inform=Video;%TimeCode_FirstFrame%", input_file]
        )
        .decode()
        .strip()
    )
    timecode_arg = f"-timecode {timecode}" if timecode else ""

    ytmov = os.path.join(youtubefolder, f"{os.path.splitext(file)[0]}.mov")
    ytmp4 = os.path.join(youtubefolder, f"{os.path.splitext(file)[0]}.mp4")
    ytmp4cc = os.path.join(youtubefolder, f"{os.path.splitext(file)[0]}-cc.mp4")
    slmov = os.path.join(salemfolder, f"{os.path.splitext(file)[0]}.mov")
    slmp4 = os.path.join(salemfolder, f"{os.path.splitext(file)[0]}.mp4")
    slmp4cc = os.path.join(salemfolder, f"{os.path.splitext(file)[0]}-cc.mp4")

    if captions:
        if os.path.exists(ytmp4):
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    ytmp4,
                    "-hide_banner",
                    "-map",
                    "0:v",
                    "-map",
                    "0:a",
                    timecode_arg,
                    "-c",
                    "copy",
                    ytmov,
                ]
            )
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    slmp4,
                    "-hide_banner",
                    "-map",
                    "0:v",
                    "-map",
                    "0:a",
                    timecode_arg,
                    "-c",
                    "copy",
                    slmov,
                ]
            )
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

        if (
            subprocess.check_output(["sed", "-n", "5p", captions]).decode().strip()[8]
            == ";"
        ):
            Isdp = "df"
        else:
            Isdp = "ndf"

        command1 = f"-tcmode=29.97{Isdp}"
        command2 = f"-command=changetcmode,59.94{Isdp}"

        mac_caption_args = [
            "/Applications/MacCaption.app/Contents/MacOS/MacCaption",
            "-omit_reading_preferences_file",
            "-movie",
            ytmov,
            command1,
            "-import=scc",
            "-displaymode=caption",
            "-ioptions=A1",
            "-input",
            captions,
            command2,
            "-addtofile=quicktime608",
            "-addtofile_target",
            ytmov,
        ]

        subprocess.run(mac_caption_args)

        mac_caption_args = [
            "/Applications/MacCaption.app/Contents/MacOS/MacCaption",
            "-omit_reading_preferences_file",
            "-movie",
            slmov,
            command1,
            "-import=scc",
            "-displaymode=caption",
            "-ioptions=A1",
            "-input",
            captions,
            "-addtofile=quicktime608",
            "-addtofile_target",
            slmov,
        ]

        subprocess.run(mac_caption_args)

        mp4box_args = [
            "/Applications/GPAC.app/Contents/MacOS/MP4Box",
            "-add",
            ytmov,
            "-lang",
            "1=Eng",
            "-lang",
            "2=eng",
            "-lang",
            "3=eng",
            "-lang",
            "4=eng",
            "-new",
            ytmp4cc,
        ]

        subprocess.run(mp4box_args)

        mp4box_args = [
            "/Applications/GPAC.app/Contents/MacOS/MP4Box",
            "-add",
            slmov,
            "-lang",
            "1=Eng",
            "-lang",
            "2=eng",
            "-lang",
            "3=eng",
            "-lang",
            "4=eng",
            "-new",
            slmp4cc,
        ]

        subprocess.run(mp4box_args)

        if not os.path.exists(f"{os.path.splitext(captions)[0]}.txt"):
            mac_caption_args = [
                "/Applications/MacCaption.app/Contents/MacOS/MacCaption",
                "-import=scc",
                "-displaymode=caption",
                "-ioptions=A1",
                "-input",
                captions,
                "-export=plaintext",
                "-output",
                f"{os.path.splitext(captions)[0]}.txt",
            ]

            subprocess.run(mac_caption_args)

        os.makedirs(os.path.join(salemfolder, "Transcripts"), exist_ok=True)

        subprocess.run(
            [
                "txt2pdf",
                f"{os.path.splitext(captions)[0]}.txt",
                os.path.join(
                    salemfolder, "Transcripts", f"{os.path.splitext(file)[0]}.pdf"
                ),
            ]
        )

        if os.path.exists(ytmp4):
            uncaptioned_folder = os.path.join(youtubefolder, "uncaptioned")
            os.makedirs(uncaptioned_folder, exist_ok=True)
            os.rename(
                ytmp4, os.path.join(uncaptioned_folder, f"{os.path.basename(ytmp4)}")
            )

        if os.path.exists(slmp4):
            uncaptioned_folder = os.path.join(salemfolder, "uncaptioned")
            os.makedirs(uncaptioned_folder, exist_ok=True)
            os.rename(
                slmp4, os.path.join(uncaptioned_folder, f"{os.path.basename(slmp4)}")
            )

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
            int(
                subprocess.check_output(
                    ["mediainfo", "--Inform=General;%Duration%", input_file]
                    .decode()
                    .strip()
                )
            )
            / 1000
        ) - 120

        if (
            subprocess.check_output(
                ["mediainfo", "--Inform=Video;%ScanType%", input_file]
            )
            .decode()
            .strip()
            != "Progressive"
        ):
            print("Video isn't Progressive... Will De-Iterlace Thumbnail.")
            for n in range(1, 31):
                rand = random.randint(60, int(duration) + 60)
                subprocess.run(
                    [
                        "ffmpeg",
                        "-ss",
                        str(rand),
                        "-i",
                        input_file,
                        "-vf",
                        "bwdif",
                        "-frames:v",
                        "1",
                        "-y",
                        os.path.join(
                            youtubefolder,
                            "thumbs",
                            f"{os.path.splitext(file)[0]}-{rand}.jpg",
                        ),
                    ]
                )
                subprocess.run(
                    [
                        "ffmpeg",
                        "-ss",
                        str(rand),
                        "-i",
                        input_file,
                        "-vf",
                        "bwdif,scale=852:480",
                        "-frames:v",
                        "1",
                        "-y",
                        os.path.join(
                            salemfolder,
                            "thumbs",
                            f"{os.path.splitext(file)[0]}-{rand}.jpg",
                        ),
                    ]
                )
        else:
            print("Video is Progressive!!! Yay!")
            for n in range(1, 31):
                rand = random.randint(60, int(duration) + 60)
                subprocess.run(
                    [
                        "ffmpeg",
                        "-ss",
                        str(rand),
                        "-i",
                        input_file,
                        "-frames:v",
                        "1",
                        "-y",
                        os.path.join(
                            youtubefolder,
                            "thumbs",
                            f"{os.path.splitext(file)[0]}-{rand}.jpg",
                        ),
                    ]
                )
                subprocess.run(
                    [
                        "ffmpeg",
                        "-ss",
                        str(rand),
                        "-i",
                        input_file,
                        "-frames:v",
                        "1",
                        "-vf",
                        "scale=852:480",
                        "-y",
                        os.path.join(
                            salemfolder,
                            "thumbs",
                            f"{os.path.splitext(file)[0]}-{rand}.jpg",
                        ),
                    ]
                )


def main():
    month = get_next_monday_month()
    weeknum = get_week_number()
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
