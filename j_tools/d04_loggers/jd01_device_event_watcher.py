"""
Device Watcher Script
This Python script monitors device connect/disconnect events on Windows using WMI.
When a device is added or removed, it prints available details from Win32_PnPEntity,
including Name, DeviceID, Description, Vendor ID, and Product ID.

Note:
- FCC ID is not typically stored in Windows system properties.
- Requires the 'wmi' Python package: pip install wmi
- Run this script as Administrator for best results.
"""

import re
import sys
import wmi
import time

def main():
    try:
        c = wmi.WMI()
    except Exception as e:
        print(f"Failed to initialize WMI: {e}")
        sys.exit(1)

    try:
        # Set up watchers for device creation and deletion events
        creation_watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_PnPEntity")
        deletion_watcher = c.watch_for(notification_type="Deletion", wmi_class="Win32_PnPEntity")
    except Exception as e:
        print(f"Failed to set up WMI watchers: {e}")
        sys.exit(1)

    print("Monitoring device connection and disconnection events. Press Ctrl+C to stop.")

    try:
        while True:
            # Check for device creation
            try:
                creation_event = creation_watcher(timeout_ms=500)
                if creation_event:
                    device = creation_event
                    print("\n[Connected]")
                    print(f"Name:        {device.Name}")
                    print(f"DeviceID:    {device.DeviceID}")
                    print(f"Description: {device.Description}")

                    # If it's a USB device, try to extract Vendor and Product ID
                    if "USB" in (device.DeviceID or "").upper():
                        vid_pid_match = re.search(r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", device.DeviceID.upper())
                        if vid_pid_match:
                            vid = vid_pid_match.group(1)
                            pid = vid_pid_match.group(2)
                            print(f"Vendor ID:   0x{vid}")
                            print(f"Product ID:  0x{pid}")
                        else:
                            print("No Vendor/Product ID found.")

                        print("FCC ID: Not available via system properties. Check device label or documentation.")
                    print("---------------------------------")
            except wmi.x_wmi_timed_out:
                pass  # No creation event within timeout

            # Check for device deletion
            try:
                deletion_event = deletion_watcher(timeout_ms=500)
                if deletion_event:
                    device = deletion_event
                    print("\n[Disconnected]")
                    print(f"Name:        {device.Name}")
                    print(f"DeviceID:    {device.DeviceID}")
                    print(f"Description: {device.Description}")
                    print("---------------------------------")
            except wmi.x_wmi_timed_out:
                pass  # No deletion event within timeout

            # Sleep briefly to prevent high CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped monitoring.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
