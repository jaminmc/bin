#!/bin/bash
DEFAULT_RESOLVE_PATH="/Applications/DaVinci Resolve/DaVinci Resolve.app"
DEFAULT_REMOTE_PATH='/Applications/DaVinci Resolve/DaVinci Remote Monitor.app'
RESOLVE_PATH="${1:-$DEFAULT_RESOLVE_PATH}"
RESOLVE_FILE="$RESOLVE_PATH/Contents/MacOS/Resolve"
HEX_VALUES_RESOLVE=(
    'A9FF84C00F8488' 'A9FFB0010F8488' # Intel
    'A9FF84C00F85' 'A9FFB0010F85'     # Intel
    'CCE8B4C1FFFF' 'CCB800000000'     # Intel
    'BD1FEB97' '20008052'             # Arm
    'BC1FEB97' '20008052'             # Arm
    'E3F2FF97E00B' '000080D2E00B'     # Arm
)
REMOTE_PATH="${1:-$DEFAULT_REMOTE_PATH}"
REMOTE_FILE="$REMOTE_PATH/Contents/MacOS/DaVinci Remote Monitor"
HEX_VALUES_REMOTE=(
    '46FBFFFFA801' '46FBFFFFB001'         # Intel
    'E8B4C1FFFF' 'B800000000'               # Intel
    'E82340B9880C' 'E8030032880C'   # Arm
    '04490094C0' '00008052C0'       # Arm
)
check_utilities() {
    utilities=("perl" "codesign" "xattr")
    for util in "${utilities[@]}"; do
        command -v "$util" >/dev/null 2>&1 || {
            echo >&2 "Error: $util is required but not installed. Try running 'xcode-select --install'"
            exit 1
        }
    done
}
hex() {
    perl -0777pe 's|([0-9a-zA-Z]{2}+(?![^\(]*\)))|\\x${1}|gs' <<<"$1"
}
hex_patch() {
    dom=$(hex "$2")
    sub=$(hex "$3")
    sudo perl -0777pi -e 'BEGIN{$/=\1e8} s|'"$dom"'|'"$sub"'|gs' "$1"
}
prep() {
    sudo xattr -r -d com.apple.quarantine "$1"
    sudo codesign --force --deep --sign - "$1"
}
patch_file() {
    local file="$1"
    local hex_values=("${@:2}")
    for ((i = 0; i < ${#hex_values[@]}; i += 2)); do
        hex_patch "$file" "${hex_values[i]}" "${hex_values[i + 1]}"
    done
}
patch_resolve() {
    patch_file "$RESOLVE_FILE" "${HEX_VALUES_RESOLVE[@]}"
}
patch_remote() {
    patch_file "$REMOTE_FILE" "${HEX_VALUES_REMOTE[@]}"
}
make_license() {
    license_content="LICENSE blackmagic davinciresolvestudio $(printf "%06d" $((RANDOM % 1000000))) permanent uncounted
  hostid=ANY issuer=CGP customer=CGP issued=$(date +"%d-%b-%Y")
  akey=$(printf "%04d-%04d-%04d-%04d-%04d" $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000)) $((RANDOM % 10000))) _ck=00 sig=\"00\""

    echo "$license_content" | sudo tee "/Library/Application Support/Blackmagic Design/DaVinci Resolve/.license/blackmagic.lic" >/dev/null
}

check_utilities
patch_resolve
patch_remote
prep "$RESOLVE_PATH"
prep "$REMOTE_PATH"
make_license