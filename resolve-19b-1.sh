#!/bin/bash
DEFAULT_APP_PATH="/Applications/DaVinci Resolve/DaVinci Resolve.app"
APP_PATH="${1:-$DEFAULT_APP_PATH}"
APP_FILE="$APP_PATH/Contents/MacOS/Resolve"
HEX_VALUES_APP=(
    'A4FF84C00F8481' 'A4FFB0010F8481' # Intel
    '8CD4A4FF84C0' '8CD4A4FFB001'     # Intel
    'CCE8B4C1FFFF' 'CCB800000000'     # Intel

    '29EFE997' '20008052'         # Arm
    '28EFE997' '20008052'         # Arm
    '08AAE3F2FF97' '08AA000080D2' # Arm
)
check_utilities() {
    local utilities=("perl" "codesign" "xattr")
    for util in "${utilities[@]}"; do
        command -v "$util" >/dev/null 2>&1 || {
            echo >&2 "Error: $util is required but not installed. try running 'xcode-select --install'"
            exit 1
        }
    done
}
hex() {
    echo "$1" | perl -0777pe 's|([0-9a-zA-Z]{2}+(?![^\(]*\)))|\\x${1}|gs'
}
hex_patch() {
    local dom sub
    dom=$(hex "$2")
    sub=$(hex "$3")
    sudo perl -0777pi -e 'BEGIN{$/=\1e8} s|'"$dom"'|'"$sub"'|gs' "$1"
}
prep() {
    sudo xattr -r -d com.apple.quarantine "$1"
    sudo codesign --force --deep --sign - "$1"
}
patch_app() {
    for ((i = 0; i < ${#HEX_VALUES_APP[@]}; i += 2)); do
        hex_patch "$APP_FILE" "${HEX_VALUES_APP[i]}" "${HEX_VALUES_APP[i + 1]}"
    done
}
check_utilities
patch_app
prep "$APP_PATH"
[[ -d "/Library/Application Support/Blackmagic Design/DaVinci Resolve/.license" ]] || sudo mkdir -p "/Library/Application Support/Blackmagic Design/DaVinci Resolve/.license"
echo "LICENSE blackmagic davinciresolvestudio $(printf "%06d" $((RANDOM % 1000000))) permanent uncounted
  hostid=ANY issuer=CGP customer=CGP issued=$(date +"%d-%b-%Y")
  akey=$(printf "%04d-%04d-%04d-%04d-%04d" $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000))) _ck=00 sig=\"00\"" | sudo tee "/Library/Application Support/Blackmagic Design/DaVinci Resolve/.license/blackmagic.lic" >/dev/null
