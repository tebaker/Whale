import sys
import os
import shutil
import argparse
import glob
import xml.etree.ElementTree as ET
import zipfile

from downloader import download_nuget_packages, TEMP_DOWNLOAD_FOLDER, NUGET_CMD
from archiver import extract_nupkg_packages, create_zip_archive

# --- Configuration ---
OUTPUT_BASE_PATH = "final_archives"

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

def main():
    """Main method to orchestrate the entire process."""
    while True:
        try:
            # Prompt user for nugets to download
            package_list_str = show_whale_prompt()
            packages = [p.strip() for p in package_list_str.split(',') if p.strip()]

            # If nothing in the packages break out to errors
            if not packages:
                print("\nProcess canceled.")
            
            # Download packages to temp_folder; will be removed after
            downloaded_count = download_nuget_packages(packages, TEMP_DOWNLOAD_FOLDER)
            
            # If nothing was downloaded freak out
            if downloaded_count == 0:
                print("\nNo packages were successfully downloaded. Exiting.")
            
            print("\nAll puup'd out. Now digesting...")

            try:
                # Extract nupkg packages from temp downloads folder
                source_folder_path = extract_nupkg_packages()

                # 1. Create archive zip and place it *inside* the source folder
                final_zip_path = create_zip_archive(source_folder_path)
        
                # 2. Use the returned path for success message
                if final_zip_path:
                    # 5. Place the readme file inside the final folder
                    # readme_path = create_readme_file(package_dependencies, final_folder)
            
                    print("\n\n" + "="*50)
                    print("🎉 WHALE-PUUP Operation Complete!")
                    print(f"Final output is located at: {source_folder_path}")
                    print(f"ZIP archive is located at: {final_zip_path}")
                    print("="*50)

            finally:
                # Clean up temporary download folder
                if os.path.exists(TEMP_DOWNLOAD_FOLDER):
                    try:
                        shutil.rmtree(TEMP_DOWNLOAD_FOLDER)
                        print(f"\n🗑️ Cleaned up temporary folder: {TEMP_DOWNLOAD_FOLDER}")
                    except OSError as e:
                        print(f"  ⚠️ Warning: Could not remove temporary folder {TEMP_DOWNLOAD_FOLDER}. {e}")
                        
        except Exception as e:
            # 7. Catch any other unexpected errors
            print(f"⚠️ An unexpected error occurred: {e}")
            sys.exit(1)















if __name__ == "__main__":
    main()
    