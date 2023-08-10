#!/bin/bash

for ks in /Volumes/*/.keepThisDriveSpinning ; do 
    if [[ "$ks" == "/Volumes/*/.keepThisDriveSpinning" ]]; then
        continue
    else
        if [ -f "$ks" ]; then
            date > "$ks"
            head -c 2097152 < /dev/urandom >> "$ks"
        fi
    fi
done
sleep 2
exit 0