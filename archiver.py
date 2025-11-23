import sys
import os
import shutil
import datetime

# --- Configuration ---
# The file extension we are looking for.
TARGET_EXTENSION = ".nupkg"
# The base directory where all the temporary download folders reside.
TEMP_DOWNLOAD_FOLDER = "temp_downloads"

def extract_nupkg_packages():
    """
    Scans subdirectories inside the 'temp_downloads' folder (relative to the
    script's location) for matching .nuget files and copies them to a new, 
    timestamped destination folder.
    
    This version correctly uses the executable's location to resolve paths, 
    ensuring it works reliably when packaged as an EXE and passed to users.
    """
    
    # 1. Determine the absolute path of the script's directory (EXE location)
    # sys.argv[0] holds the path to the executing file. os.path.dirname 
    # extracts the folder path from that file path.
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Construct the GUARANTEED input path: [EXE_DIR]/temp_downloads
    SOURCE_BASE_DIR = os.path.join(script_dir, TEMP_DOWNLOAD_FOLDER)

    
    # 2. Generate the unique, timestamped destination folder name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Construct the GUARANTEED output path: [EXE_DIR]/whale_puup_...
    DESTINATION_DIR = os.path.join(script_dir, f"whale_puup_{timestamp}")
    
    # Check if the source directory exists
    if not os.path.isdir(SOURCE_BASE_DIR):
        print(f"Error: Source directory '{SOURCE_BASE_DIR}' not found.")
        print(f"Please ensure the '{TEMP_DOWNLOAD_FOLDER}' folder is located in the same directory as this executable.")
        return

    # 3. Create the destination directory
    try:
        os.makedirs(DESTINATION_DIR, exist_ok=True)
        print(f"Created destination folder: '{DESTINATION_DIR}'")
    except Exception as e:
        print(f"Error creating destination folder: {e}")
        return

    found_count = 0
    
    # 4. Iterate through all items in the SOURCE_BASE_DIR
    for folder_name_raw in os.listdir(SOURCE_BASE_DIR):
        
        # We must use the raw folder name to access the folder path
        sub_dir_path = os.path.join(SOURCE_BASE_DIR, folder_name_raw)

        # Ensure the item is a directory before proceeding
        if os.path.isdir(sub_dir_path):
            
            # Assume file name is EXACTLY the raw folder name + extension.
            # This handles cases where directory names contain hidden whitespace.
            expected_filename = f"{folder_name_raw}{TARGET_EXTENSION}"
            source_file_path = os.path.join(sub_dir_path, expected_filename)
            
            # Print the path we are checking using os.path.join for clean separators
            print(f"\nChecking path: {source_file_path}")

            # 5. Check if the specific, expected file exists
            if os.path.isfile(source_file_path):
                # We strip the name for the final output folder to keep files clean.
                clean_filename_for_copy = f"{folder_name_raw.strip()}{TARGET_EXTENSION}"
                destination_file_path = os.path.join(DESTINATION_DIR, clean_filename_for_copy)
                
                # 6. Copy the file
                try:
                    # shutil.copy2 preserves file metadata
                    shutil.copy2(source_file_path, destination_file_path)
                    found_count += 1
                    print(f"  -> SUCCESS: Copied '{clean_filename_for_copy}' to '{DESTINATION_DIR}'")
                except Exception as e:
                    print(f"  -> ERROR copying '{clean_filename_for_copy}': {e}")
            else:
                print(f"  -> File not found at expected location.")
            
    # 7. Final summary
    print("\n--- Summary ---")
    if found_count > 0:
        print(f"Extraction complete! Copied {found_count} file(s) to '{DESTINATION_DIR}'")
    else:
        print(f"No matching {TARGET_EXTENSION} files were found.")

    return DESTINATION_DIR

def create_zip_archive(source_folder_path):
    """
    Creates a ZIP archive of the contents of the given source_folder_path
    and places the resulting ZIP file inside that same folder.
    
    Args:
        source_folder_path (str): The absolute path to the directory containing 
                                  the extracted NuGet packages.
                                  
    Returns:
        str: The absolute path to the newly created ZIP file.
    """
    print("--- NuGet Package Archiver ---")
    
    # 1. Define the base name of the ZIP file
    # We use the existing folder name (e.g., 'whale_puup_20251122_100003')
    zip_basename = os.path.basename(source_folder_path)
    
    # 2. Define the output directory for the ZIP file (which is the source folder itself)
    output_dir = source_folder_path 
    
    try:
        # shutil.make_archive parameters:
        # 1. base_name: The path/name of the output ZIP (WITHOUT the .zip extension)
        # 2. format: 'zip'
        # 3. root_dir: The directory *containing* the directory to be zipped (the parent folder)
        # 4. base_dir: The directory *to be zipped* (the source folder name itself)
        
        # We want to zip the *contents* of source_folder_path, 
        # but we need the output file to land *inside* source_folder_path.
        
        # To do this, we create the ZIP file *temporarily* outside the folder, 
        # then move it inside.
        
        # Temporary ZIP path in the parent directory
        parent_dir = os.path.dirname(source_folder_path)
        temp_zip_path = os.path.join(parent_dir, zip_basename) 
        
        # Archive the contents of the source folder
        archive_path_with_ext = shutil.make_archive(
            base_name=temp_zip_path,  # Output file name (temporarily outside)
            format='zip',
            root_dir=parent_dir,      # Start search in parent directory
            base_dir=zip_basename     # Zip the contents of this folder inside root_dir
        )
        
        # 3. Move the ZIP file into the source folder
        final_zip_name = f"{zip_basename}.zip"
        final_zip_path = os.path.join(source_folder_path, final_zip_name)
        
        # Move the newly created ZIP file into the source folder
        shutil.move(archive_path_with_ext, final_zip_path)

        print("\n--- Summary ---")
        print(f"SUCCESS: Archive created and placed inside its source folder.")
        print(f"ZIP File location: '{final_zip_path}'")
        
        return final_zip_path

    except Exception as e:
        print(f"\nError creating zip archive: {e}")
        return None

# ==============================================================================
# WHALE-PUUP Archiver Module (archiver.py)
# Handles zipping a directory and encoding the resulting zip file into Base64.
# ==============================================================================

import os
import shutil
# IMPORTANT: These imports rely on other modules existing in the same directory.
import encoder  # Assumes encoder.py has encode_file_to_base64
import utilities # Assumes utilities.py has the color function

def archive_and_encode_packages(source_dir, dest_folder):
    """
    Archives the content of the source directory into a ZIP file,
    then encodes that ZIP file into a Base64 .txt file in the destination folder.

    Args:
        source_dir (str): The directory containing files to be zipped (either
                          NuGet extracted content or user's local folder).
        dest_folder (str): The final destination path for the ZIP and Base64 files.

    Returns:
        tuple (str, str): A tuple containing the paths to the final ZIP file
                          and the final Base64 TXT file, or (None, None) on failure.
    """
    
    zip_path = None
    base64_output_path = None
    
    try:
        if not os.path.exists(source_dir):
            print(utilities.color(f"[ERROR] Source directory not found: {source_dir}", "RED"))
            return None, None

        # 1. --- Determine ZIP Filename ---
        base_name = os.path.basename(source_dir)
        zip_base = os.path.join(dest_folder, base_name)
        
        print(utilities.color(f"[ARCHIVE] Compressing contents of {base_name} into a ZIP...", "YELLOW"))

        # 2. --- Create ZIP Archive ---
        # shutil.make_archive handles creating the zip file from the directory content
        shutil.make_archive(zip_base, 'zip', source_dir)
        zip_path = zip_base + '.zip'
        
        if not os.path.exists(zip_path):
            raise Exception("ZIP creation failed unexpectedly.")
            
        print(utilities.color(f"[ARCHIVE] ZIP Archive created successfully at: {zip_path}", "GREEN"))

        # 3. --- BASE64 ENCODING ---
        base64_output_path = zip_base + ".base64.txt"
        
        print(utilities.color(f"[ENCODE] Starting Base64 encoding of {os.path.basename(zip_path)}...", "CYAN"))

        # Call the encoder module function to perform the Base64 conversion
        encoder.encode_file_to_base64(zip_path, base64_output_path)
        
        print(utilities.color(f"[ENCODE] Base64 encoding complete. File saved to: {base64_output_path}", "GREEN"))

        # 4. --- Cleanup (Remove the temporary ZIP file) ---
        print(utilities.color(f"[CLEANUP] Removing intermediate ZIP file: {zip_path}", "YELLOW"))
        os.remove(zip_path)

        return zip_path, base64_output_path

    except Exception as e:
        print(utilities.color(f"[CRITICAL ERROR in Archiver] Processing failed: {e}", "RED"))
        
        # Cleanup routine if an error occurs mid-process
        if zip_path and os.path.exists(zip_path):
            os.remove(zip_path)
        if base64_output_path and os.path.exists(base64_output_path):
            os.remove(base64_output_path)
            
        return None, None