import os
import sys
import struct
import binascii
import subprocess
import re
import json

# --- Configuration ---
# Output folder where recovered files will be saved
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "recovered_drive_data")

# Define file signatures (headers and footers) for common file types
FILE_SIGNATURES = {
    # --- Images ---
    "jpg": {
        "header": b"\xFF\xD8\xFF",
        "footer": b"\xFF\xD9",
        "extension": "jpg"
    },
    "png": {
        "header": b"\x89PNG\x0D\x0A\x1A\x0A",
        "footer": b"IEND\xAEB`\x82", # IEND chunk
        "extension": "png"
    },
    "gif": {
        "header": b"GIF89a", # or GIF87a
        "extension": "gif"
    },
    "bmp": {
        "header": b"BM",
        "extension": "bmp"
    },
    "tiff": { # Big-endian and Little-endian
        "header": b"II*\x00" or b"MM\x00*",
        "extension": "tif"
    },
    "webp": { # RIFF header followed by WEBP (usually at offset 8)
        "header": b"RIFF",
        "offset_check": 8, # Check for WEBP at this offset after RIFF
        "secondary_check": b"WEBP",
        "extension": "webp"
    },

    # --- Videos ---
    "mp4_mov": {
        "header": b"ftyp",
        "offset_check": 4, # 'ftyp' often appears at byte 4 after the size field
        "extension": "mp4" # Can be .mov too
    },
    "avi": { # RIFF header with AVI at offset 8
        "header": b"RIFF",
        "offset_check": 8,
        "secondary_check": b"AVI ",
        "extension": "avi"
    },
    "mkv": { # Matroska header
        "header": b"\x1A\x45\xDF\xA3",
        "extension": "mkv"
    },

    # --- Audio ---
    "mp3": { # Common MP3 frame sync word (variable, this is a basic one)
        "header": b"\xFF\xFB", # MPEG-1 Layer III
        "extension": "mp3"
    },
    "wav": { # RIFF header with WAVE at offset 8
        "header": b"RIFF",
        "offset_check": 8,
        "secondary_check": b"WAVE",
        "extension": "wav"
    },

    # --- Documents ---
    "pdf": {
        "header": b"%PDF",
        "footer": b"%%EOF",
        "extension": "pdf"
    },
    "docx_xlsx_pptx": { # These are actually ZIP files with specific internal structures
        "header": b"PK\x03\x04", # PK ZIP header
        # offset_check is None for these, meaning header is at offset 0
        "extension": "zip"
    },
    "rtf": {
        "header": b"{\\rtf1",
        "extension": "rtf"
    },

    # --- Archives ---
    "zip": { # General ZIP file header (PK)
        "header": b"PK\x03\x04",
        # offset_check is None for these
        "extension": "zip"
    },
    "rar": {
        "header": b"Rar!\x1A\x07\x00", # RAR 4.x header
        "extension": "rar"
    },
    "7z": {
        "header": b"7z\xBC\xAF\x27\x1C",
        "extension": "7z"
    },

    # --- Executables (Windows) ---
    "exe_dll": { # MZ header for Windows PE executables/DLLs
        "header": b"MZ",
        "extension": "exe"
    },
    
    # --- Other ---
    "sqlite": { # SQLite database header
        "header": b"SQLite format 3\x00",
        "extension": "db"
    }
}

# --- Helper Functions ---

def get_physical_drives_powershell():
    """
    Lists physical drives on Windows using PowerShell, including associated drive letters.
    """
    drives_info = []
    try:
        powershell_command = """
        $physicalDisks = Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, Size, BusType
        $partitions = Get-Partition | Select-Object DiskNumber, DriveLetter, Size, PartitionNumber, IsBoot
        $volumes = Get-Volume | Select-Object DriveLetter, FileSystem, SizeRemaining, Size, Label

        $result = @()
        foreach ($pDisk in $physicalDisks) {
            $diskPartitions = $partitions | Where-Object {$_.DiskNumber -eq $pDisk.DeviceId}
            $driveLetters = @()
            $volumeLabels = @()

            foreach ($part in $diskPartitions) {
                if ($part.DriveLetter) {
                    $driveLetters += "$($part.DriveLetter):"
                    $matchingVolume = $volumes | Where-Object {$_.DriveLetter -eq $part.DriveLetter}
                    if ($matchingVolume.Label) {
                        $volumeLabels += $matchingVolume.Label
                    }
                }
            }
            
            $driveLetterString = ""
            if ($driveLetters.Count -gt 0) {
                $driveLetterString = "(" + ($driveLetters -join ", ") + ")"
            }

            $volumeLabelString = ""
            if ($volumeLabels.Count -gt 0) {
                $volumeLabelString = "[" + ($volumeLabels -join ", ") + "]"
            }

            $result += [PSCustomObject]@{
                DeviceId = $pDisk.DeviceId
                FriendlyName = $pDisk.FriendlyName
                Size = $pDisk.Size
                BusType = $pDisk.BusType
                DriveLetters = $driveLetterString # Consolidated drive letters
                VolumeLabels = $volumeLabelString # Consolidated volume labels
            }
        }
        $result | ConvertTo-Json -Compress
        """
        
        process = subprocess.Popen(['powershell.exe', '-NoProfile', '-Command', powershell_command],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   text=True)
        
        stdout, stderr = process.communicate()

        if stderr:
            print(f"Error calling PowerShell: {stderr.strip()}")
            print("Ensure PowerShell cmdlets for Storage are available and you are running as Administrator.")
            return []

        try:
            json_output = json.loads(stdout)
            
            if isinstance(json_output, dict):
                json_output = [json_output]

            for item in json_output:
                device_id = item.get("DeviceId")
                friendly_name = item.get("FriendlyName", "Unknown Device")
                size_bytes = item.get("Size")
                bus_type = item.get("BusType", "Unknown Bus")
                drive_letters = item.get("DriveLetters", "")
                volume_labels = item.get("VolumeLabels", "")

                if device_id is not None and size_bytes is not None:
                    physical_drive_path = f"\\\\.\\PhysicalDrive{device_id}"
                    size_gb = size_bytes / (1024**3)
                    
                    description = f"{friendly_name} ({bus_type}, {size_gb:.2f} GB) {drive_letters} {volume_labels}"
                    drives_info.append({
                        "DeviceID": physical_drive_path,
                        "Caption": description,
                        "RawSize": size_bytes
                    })
        except json.JSONDecodeError as jde:
            print(f"Error decoding JSON from PowerShell output: {jde}")
            print(f"Raw PowerShell output: {stdout}")
            return []

    except FileNotFoundError:
        print("Error: 'powershell.exe' not found. Ensure PowerShell is installed and in your system PATH.")
    except Exception as e:
        print(f"An unexpected error occurred while trying to list drives with PowerShell: {e}")
    return drives_info


def select_drive():
    """Allows the user to select a physical drive for recovery."""
    print("\n--- Available Physical Drives ---")
    if sys.platform.startswith('win'):
        drives = get_physical_drives_powershell()
        if not drives:
            print("No physical drives detected or unable to retrieve detailed drive information via PowerShell.")
            print("Please ensure you are running as Administrator.")
            print("If the issue persists, you may need to manually enter the drive path (e.g., \\\\.\\PhysicalDrive0).")
            manual_path_prompt = input("Do you want to try manual drive path input? (y/n): ").lower()
            if manual_path_prompt == 'y':
                manual_path = input("Enter the raw device path manually (e.g., \\\\.\\PhysicalDrive0): ")
                return manual_path
            return None
        
        for i, drive in enumerate(drives):
            print(f"{i+1}. {drive['DeviceID']} - {drive['Caption']}")
        
        while True:
            try:
                choice = input("Enter the number of the drive to recover from: ")
                idx = int(choice) - 1
                if 0 <= idx < len(drives):
                    return drives[idx]["DeviceID"]
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print("This drive selection feature is primarily designed for Windows.")
        print("For Linux/macOS, you must manually enter the device path (e.g., /dev/sdb).")
        manual_path = input("Enter the raw device path manually (e.g., /dev/sdb): ")
        return manual_path

def create_output_folder():
    """Creates the designated output folder if it doesn't exist."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")
    else:
        print(f"Output folder already exists: {OUTPUT_FOLDER}")

def finalize_and_save_file(output_folder, file_data, sig_type, extension, file_counter_ref, reason=""):
    """Helper function to save the carved file."""
    if not file_data:
        return 0 # No data to save

    file_counter_ref[0] += 1 # Increment the counter via reference
    current_file_num = file_counter_ref[0]
    
    filename_prefix = "recovered_file"
    if reason and ("Found" in reason or "Stopped by new" in reason or "Footer found" in reason): # Give better names for known types
        filename_prefix = sig_type.replace("_", "") # e.g., "recovered_jpg"
        if not filename_prefix.startswith("recovered_"):
            filename_prefix = "recovered_" + filename_prefix

    output_filepath = os.path.join(output_folder, f"{filename_prefix}_{current_file_num}.{extension}")
    try:
        with open(output_filepath, 'wb') as out_f:
            out_f.write(file_data)
        print(f"  Saved {sig_type} to: {output_filepath} (approx. {len(file_data)/1024/1024:.2f} MB) {reason}")
        return 1
    except Exception as e:
        print(f"Error saving file {output_filepath}: {e}")
        return 0

def carve_files(device_path, output_folder, signatures):
    """
    Performs file carving by scanning the raw disk for known file signatures.
    This is a simplified approach and may not recover all files, especially fragmented ones.
    """
    print(f"\nStarting file carving from: {device_path}")
    print(f"Saving recovered files to: {output_folder}")
    print(f"Attempting to recover file types: {', '.join(signatures.keys())}")

    create_output_folder()

    recovered_count = 0
    current_file_data = b""
    is_carving = False
    current_signature_type = None
    current_file_extension = None
    file_counter = [0] # Use a list to pass by reference to allow modification in helper

    SEARCH_CHUNK_SIZE = 4096 # Search for headers in 4KB chunks
    MAX_CARVE_SIZE = 500 * 1024 * 1024 # Limit carve size (adjust as needed for very large files)
    
    buffer = b"" # Stores data read from the disk to be searched for signatures
    total_bytes_read = 0

    try:
        with open(device_path, 'rb') as f:
            while True:
                chunk = f.read(SEARCH_CHUNK_SIZE)
                if not chunk:
                    # End of disk reached. If we were carving, save the last piece.
                    if is_carving and current_file_data:
                        recovered_count += finalize_and_save_file(
                            output_folder, current_file_data, current_signature_type,
                            current_file_extension, file_counter, "End of disk (partial)"
                        )
                    break 

                total_bytes_read += len(chunk)
                buffer += chunk
                
                i = 0 
                while i < len(buffer):
                    if is_carving:
                        # --- Logic when currently carving a file ---
                        footer_found = False
                        footer = signatures[current_signature_type].get("footer")
                        
                        if footer:
                            footer_index = buffer.find(footer, i)
                            if footer_index != -1:
                                current_file_data += buffer[i : footer_index + len(footer)]
                                recovered_count += finalize_and_save_file(
                                    output_folder, current_file_data, current_signature_type,
                                    current_file_extension, file_counter, "Footer found"
                                )
                                # Consume the carved file and its footer from the buffer
                                buffer = buffer[footer_index + len(footer):]
                                i = 0 # Reset buffer index to start scanning new buffer from beginning
                                current_file_data = b""
                                is_carving = False
                                footer_found = True
                                continue # Continue with the potentially new buffer

                        if not footer_found:
                            # Search for any *new* headers within the current buffer, indicating end of current file
                            next_header_found_index = -1
                            next_header_type = None
                            
                            for check_sig_type, check_sig_info in signatures.items():
                                check_header = check_sig_info["header"]
                                # Safely get check_offset, default to 0 if not present or None
                                check_offset_val = check_sig_info.get("offset_check", 0) 
                                secondary_check = check_sig_info.get("secondary_check", None)

                                # Don't try to find the *same* header again immediately after starting carving
                                if check_sig_type == current_signature_type and (i + check_offset_val) < (len(check_header) + 16): 
                                    continue 
                                
                                potential_header_index = buffer.find(check_header, i)
                                
                                if potential_header_index != -1:
                                    is_valid_secondary = True
                                    
                                    if secondary_check: # Only check if secondary_check exists (is not None)
                                        # Ensure these calculations don't use None if check_offset_val was None
                                        secondary_start = potential_header_index + check_offset_val + len(check_header)
                                        secondary_end = secondary_start + len(secondary_check)
                                        if len(buffer) >= secondary_end and buffer[secondary_start:secondary_end] == secondary_check:
                                            pass
                                        else:
                                            is_valid_secondary = False # Secondary check failed
                                    
                                    if is_valid_secondary:
                                        # Found a new header, and it's valid
                                        if next_header_found_index == -1 or potential_header_index < next_header_found_index:
                                            next_header_found_index = potential_header_index
                                            next_header_type = check_sig_type
                            
                            if next_header_found_index != -1:
                                # Found a new header while carving the current file.
                                # Finalize and save the current file up to the point of the new header.
                                current_file_data += buffer[i : next_header_found_index]
                                recovered_count += finalize_and_save_file(
                                    output_folder, current_file_data, current_signature_type,
                                    current_file_extension, file_counter, f"Stopped by new {next_header_type} header"
                                )
                                # The buffer now starts from the new header
                                buffer = buffer[next_header_found_index:]
                                i = 0 # Reset for the new buffer
                                current_file_data = b"" # Reset current file data
                                is_carving = False # Not carving the old file anymore
                                continue # Restart the while loop with the new buffer to find the new header
                            
                            # If no footer or new header found, continue adding data, checking max size
                            remaining_buffer_segment = buffer[i:]
                            if len(current_file_data) + len(remaining_buffer_segment) >= MAX_CARVE_SIZE:
                                # Carve up to MAX_CARVE_SIZE
                                bytes_to_take = MAX_CARVE_SIZE - len(current_file_data)
                                current_file_data += remaining_buffer_segment[:bytes_to_take]
                                recovered_count += finalize_and_save_file(
                                    output_folder, current_file_data, current_signature_type,
                                    current_file_extension, file_counter, "Max size reached"
                                )
                                # The buffer starts from where we cut the file off
                                buffer = buffer[i + bytes_to_take:]
                                i = 0 # Reset for the new buffer
                                current_file_data = b""
                                is_carving = False # Finished this carve
                                continue # Continue with potentially new buffer
                            else:
                                # Add the entire remaining buffer segment to current file data
                                current_file_data += remaining_buffer_segment
                                buffer = b"" # Buffer is consumed, need to read more from disk
                                break # Break from inner while, go to outer loop to read more data
                    else:
                        # --- Logic when not currently carving (searching for new headers) ---
                        found_signature = False
                        for sig_type, sig_info in signatures.items():
                            header = sig_info["header"]
                            # Safely get search_offset, default to 0 if not present or None
                            search_offset_val = sig_info.get("offset_check", 0) 
                            secondary_check = sig_info.get("secondary_check", None)

                            # Calculate required length for header and potential secondary check safely
                            secondary_len = len(secondary_check) if secondary_check is not None else 0
                            required_len_for_check = search_offset_val + len(header) + secondary_len

                            # Ensure enough buffer is available for header and secondary check
                            if len(buffer) - i >= required_len_for_check:
                                
                                # Check main header
                                if buffer[i + search_offset_val : i + search_offset_val + len(header)] == header:
                                    is_valid_secondary = True
                                    header_capture_end = i + search_offset_val + len(header) # Initial end of capture
                                    
                                    if secondary_check: # Only check if secondary_check exists
                                        # Check secondary header
                                        secondary_start_in_buffer = i + search_offset_val + len(header)
                                        secondary_end_in_buffer = secondary_start_in_buffer + len(secondary_check)
                                        if len(buffer) >= secondary_end_in_buffer and \
                                           buffer[secondary_start_in_buffer : secondary_end_in_buffer] == secondary_check:
                                            header_capture_end = secondary_end_in_buffer # Extend capture to include secondary
                                        else:
                                            is_valid_secondary = False # Secondary check failed
                                            
                                    if is_valid_secondary:
                                        print(f"Found potential {sig_type} header at byte offset {total_bytes_read - len(buffer) + i + search_offset_val}")
                                        is_carving = True
                                        current_signature_type = sig_type
                                        current_file_extension = sig_info["extension"]
                                        
                                        # Capture the header (and any offset/secondary data) as the start of the file
                                        current_file_data = buffer[i : header_capture_end]
                                        
                                        # Trim the buffer and reset index for the next processing
                                        buffer = buffer[header_capture_end:]
                                        i = 0 # Reset to beginning of the new, trimmed buffer
                                        found_signature = True
                                        break # Found a header, stop checking other signatures for this position
                        
                        if not found_signature:
                            i += 1 # Move to the next byte to search for a header if nothing found yet

                # If the inner loop finishes and we are not carving, and the buffer is consumed,
                # it means we skipped bytes that weren't recognized as headers.
                # In this case, clear the buffer to read more data.
                if not is_carving and i >= len(buffer):
                    buffer = b""

                # If buffer is empty and we're not carving, continue reading from disk.
                # If buffer is NOT empty (meaning we either carved, or found a header),
                # the outer loop will re-evaluate the (potentially new/trimmed) buffer.
                if not buffer and not is_carving:
                    continue # Go to the next outer loop iteration to read more data

    except PermissionError:
        print(f"Error: Permission denied. Please run the script as Administrator.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Device '{device_path}' not found. Check the path and disk number.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during carving: {e}")
        # Allow the script to finish and report recovered files
        pass 

    print(f"\nCarving complete. Recovered {recovered_count} potential files.")
    print(f"Check the output folder: {OUTPUT_FOLDER}")
    if recovered_count == 0:
        print("No files were recovered. This script might not be suitable for your corruption type or file types.")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("!!! WARNING: THIS SCRIPT ATTEMPTS RAW DISK ACCESS. PROCEED WITH CAUTION !!!")
    print("!!! Ensure you run this script as an ADMINISTRATOR for it to work. !!!")
    print("!!! Using an INCORRECT PATH can lead to DATA LOSS on another drive. !!!")
    print("!!! This script cannot recover fragmented files reliably for all types. !!!")
    print("="*80 + "\n")

    selected_drive_path = select_drive()

    if selected_drive_path:
        print(f"\nYou have selected: {selected_drive_path}")
        print(f"The script will attempt to recover the following file types by searching for their headers:")
        for sig_name, sig_info in FILE_SIGNATURES.items():
            print(f"- {sig_name.upper()} (.{sig_info['extension']})")

        confirm = input("Type 'YES' to confirm and start carving, or anything else to exit: ").strip()
        if confirm == 'YES':
            carve_files(selected_drive_path, OUTPUT_FOLDER, FILE_SIGNATURES)
        else:
            print("Recovery cancelled by user.")
    else:
        print("No drive selected. Exiting.")