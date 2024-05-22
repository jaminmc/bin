#!/bin/bash
dehance_file="/Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore/DehancerPro_v2/DehancerPro_v2.pluginContents/MacOS/DehancerPro_v2"
hex() {
perl -0777pe 's|\s*([0-9a-zA-Z]{2}+(?![^\(]*\)))\s*|\\x${1}|gs' <<<"$1"
}
replace() {
file="$1"
dom=$(hex "$2")
sub=$(hex "$3")
sudo perl -0777pi -e 'BEGIN{$/=\1e8} s|'"$dom"'|'"$sub"'|gs' "$file"
}
prep() {
sudo xattr -r -d com.apple.quarantine "$dehance_file"
sudo codesign --force --sign - "$dehance_file"
}
patch() {
replace "$dehance_file" 'CDFB0994E00740F904000094' 'CDFB0994E00740F91F2003D5'
replace "$dehance_file" 'E8CF891600488B7DE8E806000000' 'E8CF891600488B7DE8E900000000'
}
patch
prep
