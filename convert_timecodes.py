#!/usr/bin/env python

import sys
import os
import re


def convert_time(timecode):
    parts = timecode.split("-")
    start, end = parts if len(parts) == 2 else (parts[0], None)

    # Split using both '.' and ':'
    start_parts = re.split("[.:]", start)
    if len(start_parts) not in (2, 3):
        return None

    hours, minutes, seconds = (
        int(start_parts[0]) if len(start_parts) == 3 else 0,
        int(start_parts[-2]),
        int(start_parts[-1]),
    )
    start_frames = hours * 3600 * 30 + minutes * 60 * 30 + seconds * 30

    if end:
        end_parts = re.split("[.:]", end)
        if len(end_parts) != len(start_parts):
            return None

        end_hours, end_minutes, end_seconds = (
            int(end_parts[0]) if len(end_parts) == 3 else 0,
            int(end_parts[-2]),
            int(end_parts[-1]),
        )
        end_frames = end_hours * 3600 * 30 + end_minutes * 60 * 30 + end_seconds * 30

        start_frames_24fps = int(start_frames * (1000 / 1001) * (24000 / 30000))
        end_frames_24fps = int(end_frames * (1000 / 1001) * (24000 / 30000))

        start_timecode_24fps = convert_to_timecode_24fps(start_frames_24fps)
        end_timecode_24fps = convert_to_timecode_24fps(end_frames_24fps)

        return f"Original: {timecode}    Converted: {start_timecode_24fps} - {end_timecode_24fps}"

    else:
        start_frames_24fps = int(start_frames * (1000 / 1001) * (24000 / 30000))
        start_timecode_24fps = convert_to_timecode_24fps(start_frames_24fps)

        return f"Original: {timecode}    Converted: {start_timecode_24fps}"


def convert_to_timecode_24fps(frame_count):
    hours, minutes, seconds, frames = (
        frame_count // (3600 * 24),
        (frame_count // (60 * 24)) % 60,
        (frame_count // 24) % 60,
        frame_count % 24,
    )
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = os.path.splitext(input_path)[0] + "-converted.txt"

    with open(input_path) as input_file, open(output_path, "w") as output:
        for line in input_file:
            converted_time = convert_time(line.strip())
            if converted_time:
                output.write(converted_time + "\n")
                print(converted_time)


if __name__ == "__main__":
    main()
