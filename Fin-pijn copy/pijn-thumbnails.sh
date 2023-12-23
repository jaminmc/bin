#!/bin/bash
for i in "$@" ; do
	if [ -e "$i" ]; then
		sourcefolder="$(cd "$(dirname "$i")"; pwd)"
		file="$(basename "$i")"
		mkdir -p "$sourcefolder/thumbs"
		infile="$i"

		duration=$(( $(mediainfo --Inform="General;%Duration%" "$i" ) /1000 - 80 ))


		if [[ $( mediainfo --Inform="Video;%ScanType%" "$infile" ) != "Progressive" ]]; then
			echo "Video isn't Progressive... Will De-Iterlace Thumbnail."
			sleep 4
			for n in {1..20}; do
				rand=$(( RANDOM % duration ))
				rand=$(( rand + 20 ))
				ffmpeg -hide_banner -ss $rand -i "$i" -vf "bwdif" -frames:v 1 -y "$sourcefolder/thumbs/${file%.*}-$rand.jpg" # 2> /dev/null
			done
		else
			echo "Video $file is Progressive!!! Yay!"
			sleep 4
			for n in {1..20}; do
				# rand="$(( $RANDOM % 1680 ))"
				rand=$(( RANDOM % duration ))
				ffmpeg -hide_banner -ss $rand -i "$i" -frames:v 1 -y "$sourcefolder/thumbs/${file%.*}-$rand.jpg" # 2> /dev/null
			done
		fi

	else
		echo "$i Does not exist!!! "
	fi
done
