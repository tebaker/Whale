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
TEMP_DOWNLOAD_FOLDER = "temp_nuget_downloads"
OUTPUT_BASE_PATH = "C:\\"

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

# Download Logic
def download_nuget_packages(packages, temp_folder):
    """Executes nuget install for each package with recursive dependencies."""
    if not packages:
        print("No packages specified. Aborting download.")
        return 0

    os.makedirs(temp_folder, exist_ok=True)
    success_count = 0
    
    print(f"\n🐋 Starting download of {len(packages)} packages into: {temp_folder}...")

    for package_name in packages:
        try:
            # Command to install package and its dependencies recursively
            command = [
                NUGET_CMD, 
                'install', 
                package_name,
                '-OutputDirectory', 
                temp_folder, 
                '-Recursive'
            ]
            
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"  ✅ Downloaded: {package_name}")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ ERROR downloading {package_name}. Check NuGet source/version.")
            print(f"     Output: {e.stderr.strip()}")
        except FileNotFoundError:
            print(f"  ❌ ERROR: '{NUGET_CMD}' not found. Make sure nuget.exe is in your PATH.")
            sys.exit(1)
            
    return success_count

# --- STEP 3: DOCUMENTATION LOGIC ---

def get_dependencies_from_local_folder(temp_folder):
    """Parses local .nuspec files to extract dependency information."""
    package_data = {}
    
    # Walk through the temp folder where packages are downloaded
    for item in os.listdir(temp_folder):
        item_path = os.path.join(temp_folder, item)
        if os.path.isdir(item_path):
            # Find the .nuspec file
            nuspec_files = [f for f in os.listdir(item_path) if f.endswith('.nuspec')]
            
            if nuspec_files:
                nuspec_path = os.path.join(item_path, nuspec_files[0])
                package_name_version = item 
                
                try:
                    tree = ET.parse(nuspec_path)
                    root = tree.getroot()
                    
                    # Find metadata and dependencies nodes, handling different namespaces
                    namespaces = [
                        '{http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd}',
                        '{http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd}'
                    ]
                    
                    metadata_node = None
                    dependencies_node = None
                    
                    for ns in namespaces:
                        metadata_node = root.find(f'{ns}metadata')
                        if metadata_node is not None:
                            dependencies_node = metadata_node.find(f'{ns}dependencies')
                            break

                    dependencies = []
                    if dependencies_node is not None:
                        for dep_group in dependencies_node.findall(f'{ns}group'):
                            # Handle dependency groups (e.g., for different target frameworks)
                            target = dep_group.get('targetFramework', 'All Frameworks')
                            dependencies.append(f"--- Group: {target} ---")
                            for dep in dep_group.findall(f'{ns}dependency'):
                                dep_id = dep.get('id')
                                dep_version = dep.get('version', 'Any')
                                dependencies.append(f"{dep_id} (Version: {dep_version})")
                        
                        # Handle flat dependencies
                        if not dependencies: # Only check flat if groups weren't found/processed
                             for dep in dependencies_node.findall(f'{ns}dependency'):
                                dep_id = dep.get('id')
                                dep_version = dep.get('version', 'Any')
                                dependencies.append(f"{dep_id} (Version: {dep_version})")


                    package_data[package_name_version] = dependencies

                except Exception as e:
                    package_data[package_name_version] = [f"Error reading dependencies: {e}"]

    return package_data

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

# --- STEP 4: ZIPPING AND FINALIZATION ---

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
            print("❌ DOWNLOAD FAILED.")
            print(f"Error Message from NuGet: {e.stderr.strip()}")
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

# --- MAIN METHOD ---
def main():
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
            
            # 3. Success: If the function completes without raising an exception
            print("✅ SUCCESS! Package and dependencies downloaded.")
            # Optional: Print the success output
            # print("--- Command Output ---\n", output)
            
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


if __name__ == "__main__":
    main()