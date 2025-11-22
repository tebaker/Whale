import subprocess
import os
import sys
import datetime
import base64
import argparse
import shutil
import xml.etree.ElementTree as ET

# --- Configuration ---
# You must have nuget.exe accessible in your system's PATH
NUGET_CMD = r'C:\Program Files (x86)\NuGet\nuget.exe'
# The base directory where all the temporary download folders reside.
RAW_SOURCE_DIR_NAME = "temp_downloads"
OUTPUT_BASE_PATH = "C:\\"
# The file extension we are looking for.
TARGET_EXTENSION = ".nupkg"

def show_whale_prompt():
    """Displays the ASCII whale and prompts the user for package names."""
    whale_ascii = r"""
         ,.-"`^`-.
        /   _   _  \
       /   `(o)(o)` \
      |         w  / |
      | |   `----'| |
      | |    .'"`^`".
      \ \  / .'"`^`".\
        \ `|  ./  ./
          `'-----'`  
    """
    print("\n" + "="*50)
    print("Welcome to WHALE-PUUP Download Utility!")
    print(whale_ascii)
    print("Please list the NuGet packages (comma-delimited) you need.")
    print("Example: Newtonsoft.Json, Microsoft.Extensions.Logging")
    print("="*50)
    
    # Check for command line arguments first
    if len(sys.argv) > 1:
        package_list_str = " ".join(sys.argv[1:])
        print(f"Using packages from command line: {package_list_str}\n")
    else:
        package_list_str = input("Enter package names: ")
    
    return package_list_str.strip()

def create_readme_file(package_dependencies, output_folder):
    """Creates the 'readme_puup_file.txt' with documentation."""
    file_name = "readme_puup_file.txt"
    output_path = os.path.join(output_folder, file_name)
    
    all_dependencies = set()
    
    with open(output_path, 'w') as f:
        f.write("--- Downloaded NuGet Packages and Dependencies ---\n\n")
        f.write(f"## 📦 Requested Packages and Their Dependencies ({len(package_dependencies)} items):\n")

        for pkg, deps in package_dependencies.items():
            f.write(f"* **{pkg}**\n")
            if deps and not deps[0].startswith("Error"):
                for dep in deps:
                    f.write(f"  - {dep}\n")
                    if not dep.startswith("--- Group:"):
                        all_dependencies.add(dep.split(' (Version:')[0]) # Add just the ID
            elif not deps:
                 f.write(f"  - No direct dependencies listed in metadata.\n")
            else:
                f.write(f"  - {deps[0]}\n")
        
        f.write("\n" + "="*50 + "\n\n")
        
        f.write(f"## ⚙️ All Unique Dependencies Referenced ({len(all_dependencies)} items):\n")
        for dep_id in sorted(list(all_dependencies)):
            f.write(f"* {dep_id}\n")

    return output_path

def create_final_archive(temp_folder, final_folder_path, package_count):
    """Zips the downloaded files and renames the folder/zip."""
    
    # 1. Create the timestamped folder name
    now = datetime.datetime.now()
    # Format: YYYYMMDDHHMMSS (no colons or other symbols)
    timestamp_str = now.strftime("%Y%m%d%H%M%S")
    folder_name = f"whale_puup_{package_count}_krills_at_{timestamp_str}"
    
    final_output_path = os.path.join(final_folder_path, folder_name)
    os.makedirs(final_output_path, exist_ok=True)
    
    print(f"\n🐳 Creating final output folder at: {final_output_path}")

    # 2. Create the ZIP file
    # The zip name is based on the folder name
    base_zip_name = os.path.join(final_output_path, folder_name)
    zip_path = shutil.make_archive(
        base_name=base_zip_name, 
        format='zip', 
        root_dir=temp_folder # Zip the contents of the temporary folder
    )

    # 3. Rename the .zip to .txt as requested (Warning: This is for compliance only)
    # NOTE: The content is still a ZIP archive, not plain text.
    final_zip_name = f"{folder_name}.txt"
    final_zip_path = os.path.join(final_output_path, final_zip_name)
    os.rename(zip_path, final_zip_path)
    
    print(f"  📦 Zipped all content to: {final_zip_path}")
    print(f"  ⚠️ Note: The file is a ZIP archive renamed to .txt.")
    
    return final_output_path

def download_packages(package_list, download_dir):
    print("Puuping:\n")
    for package_name in package_list:
        """
        Attempts to download a single NuGet package.
        If it fails, it prints an error and returns None, exiting the function.
        """
        print(f"\t{package_name}\n")
    
        cmd_args = [
            NUGET_CMD, 
            'install', 
            package_name, 
            '-OutputDirectory', 
            download_dir
        ]

        try:
            # Execute the command. 'check=True' will raise CalledProcessError on failure.
            result = subprocess.run(
                cmd_args, 
                capture_output=True, 
                text=True, 
                check=True  
            )
        
        except subprocess.CalledProcessError as e:
            # 1. Error handling: Print failure message
            print("❌ Nothing; I'm all backed up from {e.stderr.strip()}\n")
            print("Please check the package name or version.")
        
            # 2. Key Action: Exit the function and return control to the caller (main)
            # We return None to signal failure, but any value will work.
            return None 
        
        except FileNotFoundError:
            # Handle the case where the nuget.exe path is wrong
            print(f"🛑 CRITICAL ERROR: Could not find nuget.exe at path: {NUGET_CMD}")
            return None
        
    # If successful, return the output (or a success indicator)
    return result.stdout

def encode_file_to_base64(input_filepath, output_filepath):
    """
    Reads a binary file, encodes its content to Base64, and writes the
    resulting ASCII string to a new output file.

    The Base64 encoding process ensures that the binary data is converted
    into a format safe for transmission or storage in text-only systems.
    """
    print(f"--- Encoding Process ---")
    print(f"Input File: {input_filepath}")
    
    # --- 1. Read the input file in binary mode ---
    try:
        # Use 'rb' (read binary) mode to read the file as raw bytes.
        with open(input_filepath, 'rb') as f:
            binary_data = f.read()
        print(f"Successfully read {len(binary_data)} bytes.")

    except FileNotFoundError:
        print(f"Error: The input file '{input_filepath}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return

    # --- 2. Encode the binary data to Base64 ---
    # base64.b64encode takes a bytes object and returns an encoded bytes object.
    encoded_bytes = base64.b64encode(binary_data)
    
    # Convert the encoded bytes (e.g., b'VGhpcyBpcy...') to a string
    # using 'ascii' decoding, as Base64 output is always ASCII characters.
    encoded_content = encoded_bytes.decode('ascii')
    
    print("Content successfully Base64 encoded.")

    # --- 3. Write the Base64 string to the output file ---
    try:
        # Use 'w' (write text) mode to write the Base64 string.
        with open(output_filepath, 'w') as f:
            f.write(encoded_content)
        
        # Calculate size comparison
        original_size_kb = os.path.getsize(input_filepath) / 1024
        encoded_size_kb = os.path.getsize(output_filepath) / 1024
        
        print(f"Output File: {output_filepath}")
        print(f"Original size: {original_size_kb:.2f} KB")
        print(f"Encoded size: {encoded_size_kb:.2f} KB (Base64 adds ~33% overhead)")
        print(f"\nSuccess! The Base64 encoded content is saved to '{output_filepath}'")

    except Exception as e:
        print(f"An error occurred while writing the output file: {e}")

def extract_nupkg_files():
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
    SOURCE_BASE_DIR = os.path.join(script_dir, RAW_SOURCE_DIR_NAME)

    
    # 2. Generate the unique, timestamped destination folder name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Construct the GUARANTEED output path: [EXE_DIR]/whale_puup_...
    DESTINATION_DIR = os.path.join(script_dir, f"whale_puup_{timestamp}")
    
    # Check if the source directory exists
    if not os.path.isdir(SOURCE_BASE_DIR):
        print(f"Error: Source directory '{SOURCE_BASE_DIR}' not found.")
        print(f"Please ensure the '{RAW_SOURCE_DIR_NAME}' folder is located in the same directory as this executable.")
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

def yee():
    """Main method to orchestrate the entire process."""
    while True:
        try:
             # 1. Get package input from user/command line
            package_list_str = show_whale_prompt()
            packages = [p.strip() for p in package_list_str.split(',') if p.strip()]
            if not packages:
                print("\nProcess canceled.")
                continue
            
            # 2. Call the function that might throw an exception
            output = download_packages(packages, 'temp_downloads')
         
            # 4. Break the loop only on success
            break 
            
        except subprocess.CalledProcessError as e:
            # 5. Handle the specific error thrown by subprocess (NuGet failure)
            print("❌ DOWNLOAD FAILED. An error occurred while running nuget.exe.")
            print(f"Error Message: {e.stderr.strip()}")
            print("\nPlease check the package name, version, or network connection, and try again.")
            
        except FileNotFoundError:
            # 6. Handle the error if nuget.exe itself can't be found
            print(f"🛑 CRITICAL ERROR: Could not find nuget.exe at path: {NUGET_CMD}")
            print("Please correct the path in the script and restart.")
            break # Exit the loop as this error is not recoverable by retrying

        except Exception as e:
            # 7. Catch any other unexpected errors
            print(f"⚠️ An unexpected error occurred: {e}")
            print("Retrying download...")
            
    print("\nAll puup'd out.")

    # 1. Get package input from user/command line
    
    package_list_str = show_whale_prompt()
    packages = [p.strip() for p in package_list_str.split(',') if p.strip()]
    if not packages:
        print("\nProcess canceled.")
        return

    try:
        # 2. Download packages to temp folder
        downloaded_count = download_nuget_packages(packages, TEMP_DOWNLOAD_FOLDER)
        if downloaded_count == 0:
            print("\nNo packages were successfully downloaded. Exiting.")
            return

        # 3. Document dependencies
        package_dependencies = get_dependencies_from_local_folder(TEMP_DOWNLOAD_FOLDER)

        # 4. Create the final archive (Zip and rename)
        final_folder = create_final_archive(
            temp_folder=TEMP_DOWNLOAD_FOLDER,
            final_folder_path=OUTPUT_BASE_PATH,
            package_count=downloaded_count
        )
        
        # 5. Place the readme file inside the final folder
        readme_path = create_readme_file(package_dependencies, final_folder)
        
        print("\n\n" + "="*50)
        print("🎉 WHALE-PUUP Operation Complete!")
        print(f"Final output is located at: {final_folder}")
        print(f"File listing dependencies: {os.path.basename(readme_path)}")
        print("="*50)

    finally:
        # Clean up temporary download folder
        if os.path.exists(TEMP_DOWNLOAD_FOLDER):
            try:
                shutil.rmtree(TEMP_DOWNLOAD_FOLDER)
                print(f"\n🗑️ Cleaned up temporary folder: {TEMP_DOWNLOAD_FOLDER}")
            except OSError as e:
                print(f"  ⚠️ Warning: Could not remove temporary folder {TEMP_DOWNLOAD_FOLDER}. {e}")

def main():
    extract_nupkg_files()

if __name__ == "__main__":
    main()
    