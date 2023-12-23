#!/usr/bin/env python3
import json
import os


filename = "~/Library/Application Support/balena-etcher/config-drive.json"
newfile = "~/Library/Application Support/balena-etcher/config.json"
with open(os.path.expanduser(filename), "r") as f:
    data = json.load(f)
    blocklist = data["driveBlacklist"]
    blocklistdev = []
    for x in blocklist:
        y = os.path.realpath(x)
        # print("x=" + x + "\ny=" + y)
        if os.path.exists(x):
            blocklistdev.append(y)
data["driveBlacklist"] = blocklistdev
with open(os.path.expanduser(newfile), "w") as f:
    json.dump(data, f, indent=2)
    print("Added " + ", ".join(str(e) for e in blocklistdev) + " to etcher blocklist.")
