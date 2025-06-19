import os
import sys
import struct
import binascii

# --- Configuration ---
# !!! VERY IMPORTANT: THIS HAS BEEN UPDATED TO PhysicalDrive3 !!!
# If your SD card is "Disk 3" in Windows Disk Management, this is the correct path.
# BE EXTREMELY CAREFUL. WRONG PATH = DATA LOSS ON ANOTHER DRIVE.
SD_CARD_RAW_DEVICE_PATH = r"\\.\PhysicalDrive3"

# Output folder where recovered files will be saved
OUTPUT_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads", "recovered_sd_card_data")

# Define file signatures (headers and footers) for common camera files
# These are simplified and may not catch all variations or fragmented files.
# More robust carving software has extensive databases of these.
FILE_SIGNATURES = {
    "jpg": {
        "header": b"\xFF\xD8\xFF",
        "footer": b"\xFF\xD9",
        "extension": "jpg"
    },
    # Common header for MP4/MOV based on ftyp atom (often 4 bytes into the atom)
    # Note: Simple carving for video is very unreliable due to fragmentation and complex structures.
    # This will just attempt to capture data after 'ftyp' for a fixed size or until next header.
    "mp4_mov_base": {
        "header": b"ftyp",
        "offset_check": 4, # Check if 'ftyp' is 4 bytes in (after the size field)
        "extension": "mp4" # Could be .mov too, hard to tell without deeper parsing
    },
    "nef": { # Nikon RAW (example start, highly variable)
        "header": b"II*\x00\x10\x00\x00\x00CR\x02\x00\x00\x00",
        "extension": "nef"
    },
    "cr2": { # Canon RAW (example start, highly variable)
        "header": b"II*\x00\x08\x00\x00\x00CR\x02\x00\x00\x00",
        "extension": "cr2"
    },
    # You can add more signatures here if you know them for other file types
    # For example, BMP, GIF, PNG, etc., but remember the limitations of simple carving.
}

# --- Script Logic ---

def create_output_folder():
    """Creates the designated output folder if it doesn't exist."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}")
    else:
        print(f"Output folder already exists: {OUTPUT_FOLDER}")

def carve_files(device_path, output_folder, signatures):
    """
    Performs file carving by scanning the raw disk for known file signatures.
    This is a simplified approach and may not recover all files, especially fragmented ones.
    """
    print(f"\nStarting file carving from: {device_path}")
    print(f"Saving recovered files to: {output_folder}")

    create_output_folder()

    recovered_count = 0
    current_file_data = b""
    is_carving = False
    current_signature_type = None
    current_file_extension = None
    file_counter = 0

    # Read the disk in smaller blocks to find headers, then switch to larger chunks for body.
    SEARCH_CHUNK_SIZE = 4096 # Search for headers in 4KB chunks
    READ_BODY_CHUNK_SIZE = 10 * 1024 * 1024 # Read up to 10MB at a time for the file body once a header is found

    buffer = b"" # Stores data read from the disk to be searched for signatures
    total_bytes_read = 0

    try:
        with open(device_path, 'rb') as f:
            while True:
                chunk = f.read(SEARCH_CHUNK_SIZE)
                if not chunk:
                    break # End of disk

                total_bytes_read += len(chunk)
                buffer += chunk

                # Iterate through buffer to find signatures
                i = 0
                while i < len(buffer):
                    found_signature = False
                    for sig_type, sig_info in signatures.items():
                        header = sig_info["header"]
                        # Adjust search to allow for offset_check for certain types (e.g., 'ftyp' in MP4)
                        search_offset = 0
                        if "offset_check" in sig_info:
                            search_offset = sig_info["offset_check"]

                        # Ensure we have enough data in the buffer to check for the header at the potential offset
                        if len(buffer) - i >= search_offset + len(header):
                            if buffer[i + search_offset : i + search_offset + len(header)] == header:
                                # Found a potential header
                                print(f"Found potential {sig_type} header at byte offset {total_bytes_read - len(buffer) + i + search_offset}")
                                is_carving = True
                                current_signature_type = sig_type
                                current_file_extension = sig_info["extension"]
                                current_file_data = b"" # Start new file data for this carve
                                i += search_offset + len(header) # Move past the header in the buffer
                                found_signature = True
                                break # Found a header, stop checking other signatures for this position

                    if found_signature:
                        # Once a header is found, try to read the body.
                        # This is a very simplistic carving approach.
                        if current_signature_type == "jpg":
                            footer = signatures["jpg"]["footer"]
                            # Keep reading chunks until footer is found or end of disk
                            while True:
                                footer_index = buffer.find(footer, i)
                                if footer_index != -1:
                                    # Found footer, capture data including footer
                                    current_file_data += buffer[i : footer_index + len(footer)]
                                    file_counter += 1
                                    output_filepath = os.path.join(output_folder, f"recovered_file_{file_counter}.{current_file_extension}")
                                    with open(output_filepath, 'wb') as out_f:
                                        out_f.write(current_file_data)
                                    print(f"Recovered {current_signature_type} to: {output_filepath} ({len(current_file_data)/1024:.2f} KB)")
                                    recovered_count += 1
                                    is_carving = False
                                    buffer = buffer[footer_index + len(footer):] # Keep remaining buffer for next search
                                    i = 0 # Reset search index for the new buffer
                                    break # Done with this file, look for next header
                                else:
                                    # Footer not found in current buffer, append remaining buffer and read more
                                    current_file_data += buffer[i:]
                                    buffer = b"" # Clear buffer, it's been consumed into current_file_data
                                    new_chunk = f.read(READ_BODY_CHUNK_SIZE) # Read a larger chunk for the file body
                                    if not new_chunk:
                                        # End of disk, save partial file if any data was collected
                                        if current_file_data:
                                            print(f"Warning: Reached end of disk, saving partial {current_signature_type} file.")
                                            file_counter += 1
                                            output_filepath = os.path.join(output_folder, f"partial_recovered_file_{file_counter}.{current_file_extension}")
                                            with open(output_filepath, 'wb') as out_f:
                                                out_f.write(current_file_data)
                                            recovered_count += 1
                                        is_carving = False
                                        break # End of disk, break out of inner while True
                                    total_bytes_read += len(new_chunk)
                                    buffer += new_chunk
                                    i = 0 # Reset search index for the new buffer (as we filled it)

                        else: # For MP4/MOV/NEF/CR2 etc., which don't have simple fixed footers or are fragmented
                            # We'll read a fixed maximum amount, or until the next known header is found.
                            # This is the weakest part of simple carving and very unreliable for full video/RAW recovery.
                            MAX_CARVE_SIZE = 500 * 1024 * 1024 # Try to carve up to 500MB for non-JPGs (adjust as needed for larger files)
                            bytes_carved = 0
                            temp_file_body_buffer = b"" # Buffer to temporarily hold the file's body data
                            temp_buffer_idx = 0

                            # Start with remaining part of current main buffer
                            temp_file_body_buffer += buffer[i:]
                            bytes_carved += len(buffer[i:])
                            i = len(buffer) # Advance main buffer index past what's been taken

                            while bytes_carved < MAX_CARVE_SIZE:
                                next_chunk = f.read(READ_BODY_CHUNK_SIZE)
                                if not next_chunk:
                                    break # End of disk

                                total_bytes_read += len(next_chunk)
                                temp_file_body_buffer += next_chunk
                                bytes_carved += len(next_chunk)

                                # Simple heuristic: if we find another header *within* this file, stop.
                                # This helps prevent carving beyond one file into the next.
                                # This is still very basic and prone to error.
                                new_header_found_in_body = False
                                for check_sig_type, check_sig_info in signatures.items():
                                    check_header = check_sig_info["header"]
                                    if check_sig_type != current_signature_type: # Don't detect our own header type again
                                        check_index = temp_file_body_buffer.find(check_header, temp_buffer_idx)
                                        if check_index != -1:
                                            # Found a new header, this file probably ends here
                                            current_file_data = temp_file_body_buffer[:check_index]
                                            print(f"Stopping {current_signature_type} carve early, found {check_sig_type} header at offset {check_index} within file.")
                                            # Put the rest back into the main buffer for next iteration
                                            buffer = temp_file_body_buffer[check_index:]
                                            i = 0 # Reset main buffer index
                                            new_header_found_in_body = True
                                            break # Break from signature check loop

                                if new_header_found_in_body:
                                    break # Break out of the while loop for carving this file body

                                temp_buffer_idx = len(temp_file_body_buffer) # Advance search index for next check

                            if not current_file_data and temp_file_body_buffer: # If didn't break due to finding a new header, capture whatever was carved
                                current_file_data = temp_file_body_buffer
                                buffer = b"" # Clear the main buffer, its contents were processed into temp_file_body_buffer

                            if current_file_data:
                                file_counter += 1
                                output_filepath = os.path.join(output_folder, f"recovered_file_{file_counter}.{current_file_extension}")
                                with open(output_filepath, 'wb') as out_f:
                                    out_f.write(current_file_data)
                                print(f"Recovered {current_signature_type} to: {output_filepath} (approx. {len(current_file_data)/1024/1024:.2f} MB)")
                                recovered_count += 1
                            is_carving = False
                            current_file_data = b"" # Reset for next carve
                            # The main loop continues with the remaining 'buffer'

                    else: # No signature found at current 'i' position in buffer
                        i += 1 # Move to the next byte to search for a header

                # If the buffer is exhausted and we're not actively carving a file, clear it.
                if not is_carving and i >= len(buffer):
                    buffer = b""

    except PermissionError:
        print(f"Error: Permission denied. Please run the script as Administrator.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Device '{device_path}' not found. Check the path and disk number.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the device: {e}")
        # Continue to process whatever was found, but indicate the error
        pass # Allow the script to finish and report recovered files

    print(f"\nCarving complete. Recovered {recovered_count} potential files.")
    print(f"Check the output folder: {output_folder}")
    if recovered_count == 0:
        print("No files were recovered. This script might not be suitable for your corruption type or file types.")

if __name__ == "__main__":
    if not sys.platform.startswith('win'):
        print("This script is designed for Windows due to raw device path handling ('\\\\.\\PhysicalDriveX').")
        print("For Linux/macOS, raw device paths are typically /dev/sdX or /dev/diskX.")
        print("Modify SD_CARD_RAW_DEVICE_PATH accordingly for non-Windows OS if attempting to adapt.")
        # Example for Linux: SD_CARD_RAW_DEVICE_PATH = "/dev/sdb" (BE EXTREMELY CAREFUL!)

    print("\n" + "="*80)
    print("!!! WARNING: THIS SCRIPT ATTEMPTS RAW DISK ACCESS. PROCEED WITH CAUTION !!!")
    print("!!! Ensure you run this script as an ADMINISTRATOR for it to work. !!!")
    print(f"!!! DOUBLE-CHECK THAT '{SD_CARD_RAW_DEVICE_PATH}' IS YOUR SD CARD. !!!")
    print("!!! Using an INCORRECT PATH can lead to DATA LOSS on another drive. !!!")
    print("="*80 + "\n")
    input("Press Enter to acknowledge warnings and start carving, or close this window if you are unsure.")

    carve_files(SD_CARD_RAW_DEVICE_PATH, OUTPUT_FOLDER, FILE_SIGNATURES)