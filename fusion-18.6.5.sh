#!/bin/bash
DEFAULT_APP_PATH='/Applications/Blackmagic Fusion 18/Fusion.app'
APP_PATH="${1:-$DEFAULT_APP_PATH}"
APP_FILE="$APP_PATH/Contents/Libraries/libfusionsystem.dylib"
HEX_VALUES_APP=(
    'E8B4C1FFFF' 'B800000000'     # Intel
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
