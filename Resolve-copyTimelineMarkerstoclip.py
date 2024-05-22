# Import necessary modules
import os
import sys

sys.path.append(
    "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
)
import DaVinciResolveScript as bmd

# Create Resolve script instance
resolve = bmd.scriptapp("Resolve")

if resolve:
    # Get current project
    projectManager = resolve.GetProjectManager()
    project = projectManager.GetCurrentProject()

    if project:
        # Get media pool
        mediaPool = project.GetMediaPool()

        # Get the root folder of the media pool
        rootFolder = mediaPool.GetRootFolder()

        # Find clip named "Laugh Tracks" in the media pool
        clips = rootFolder.GetClipList()
        for clip in clips:
            if clip.GetName() == "Laugh Tracks-":
                # Get markers from the current timeline
                timeline = project.GetCurrentTimeline()
                markers = timeline.GetMarkers()
                clipmarkers = clip.GetMarkers()
                print(f"Clip markers: {clipmarkers}")
                # print(f"Timeline markers: {markers}")
                # Iterate through markers
                for frameId in markers:
                    name = markers[frameId]['name']
                    note = markers[frameId]['note']
                    color = markers[frameId]['color']
                    duration = markers[frameId]['duration']
                    # print(f"Marker: id {frameId}, name: {name}, note: {note}, color:{color}, Duration: {duration}")
                    clip.AddMarker(frameId, color, name, note, duration)
                    print(f"Marker {frameId} added to clip {clip.GetName()}")
                # for marker in markers:
                #     # Get marker information
                #     markerName = marker.GetName()
                #     markerPosition = marker.GetPosition()

                #     # Add marker to the clip
                #     clip.AddMarker(markerPosition, markerName)

                # print("Markers copied to 'Laugh Tracks' clip successfully.")
                # break  # Exit loop once the clip is found and markers are added
            # else:
            #     print("Clip 'Laugh Tracks' not found in the media pool.")
    else:
        print("No active project found.")
else:
    print("DaVinci Resolve is not running.")
