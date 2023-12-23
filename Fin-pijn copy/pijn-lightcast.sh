#!/bin/bash
for i in "$@" ; do
	if [ -e "$i" ]; then
		srcfolder="$(cd "$(dirname "$i")"; pwd)"
		file="$(basename "$i")"
		lightcastfolder="$srcfolder/LightCast"
		if [ ! -d "$lightcastfolder" ]; then
			mkdir -p "$lightcastfolder"
		fi
		nice ffmpeg -i "$i" -map 0:v -map 0:a?  -b:a 192K -metadata xmp= -vf yadif=1:0,scale=1280:720 -y -pix_fmt yuv420p -loglevel verbose -g 180 -maxrate:v 8M -bufsize:v 8M -aspect 16:9 -c:v libx264 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -crf 16 -x264opts ref=4:qpmin=4 -movflags +faststart "$lightcastfolder/${file%.*}"-720p.m4v
		# ffmpeg -i "$i" -map 0:v -map 0:a?  -b:a 192K -metadata xmp= -vf yadif=1:0,scale=1280:720 -y -pix_fmt yuv420p -loglevel verbose -g 180 -maxrate:v 8M -bufsize:v 8M -aspect 16:9 -c:v libx264 -crf 16 -x264opts ref=4:qpmin=4:colorprim=bt709:transfer=bt709:colormatrix=bt709 -movflags +faststart "$lightcastfolder/${file%.*}"-720p.m4v
	else
		echo "$i Does not exist!!! "
	fi
done
