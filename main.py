# main.py

import sys
import os
import shutil

# Import from local modules
from downloader import download_nuget_packages, TEMP_DOWNLOAD_FOLDER, NUGET_CMD
from archiver import extract_nupkg_packages, create_zip_archive
from utilities import show_whale_prompt

# --- Configuration (Centralized) ---
OUTPUT_BASE_PATH = "final_archives"

def main():
    """Main method to orchestrate the entire process."""
    # Note: We remove the 'while True' loop here to ensure the script terminates 
    # after one attempt, which is standard for command-line utilities.
    # If the user wants to run again, they execute the script again.
    
    source_folder_path = None # Initialize variable for scope
    
    try:
        # Prompt user for nugets to download. The function handles 'exit' input.
        packages = show_whale_prompt() 
        
        # Check for user cancellation or empty input (show_whale_prompt should return None or [] on cancel/invalid)
        if not packages:
            print("\nProcess canceled or no valid packages entered. Exiting.")
            sys.exit(0) # Clean exit
            
        # --- PHASE 1: DOWNLOAD ---
        downloaded_count = download_nuget_packages(packages, TEMP_DOWNLOAD_FOLDER)
            
        if downloaded_count == 0:
            print("\n❌ No packages were successfully downloaded. Exiting with error.")
            sys.exit(1) # Error exit
            
        print("\nAll puup'd out. Now digesting...")

        # --- PHASE 2: EXTRACT & ARCHIVE ---
        
        # Extract nupkg packages from temp downloads folder
        # NOTE: extract_nupkg_packages MUST return the absolute path to the output folder.
        source_folder_path = extract_nupkg_packages()

        # Create archive zip and place it *inside* the source folder
        final_zip_path = create_zip_archive(source_folder_path)
    
        # --- PHASE 3: SUCCESS MESSAGE ---
        if final_zip_path:
            print("\n\n" + "="*50)
            print("🎉 WHALE-PUUP Operation Complete!")
            print(f"Final output folder: {source_folder_path}")
            print(f"ZIP archive: {final_zip_path}")
            print("="*50)
        
    except Exception as e:
        # Catch any unexpected errors during the process
        print(f"\n⚠️ A CRITICAL and unexpected error occurred: {e}")
        print("Please check your input and configuration files.")
        sys.exit(1) # Error exit

    finally:
        # --- PHASE 4: CLEANUP ---
        # This runs regardless of success or failure in the 'try' block
        if os.path.exists(TEMP_DOWNLOAD_FOLDER):
            try:
                shutil.rmtree(TEMP_DOWNLOAD_FOLDER)
                print(f"\n🗑️ Cleaned up temporary folder: {TEMP_DOWNLOAD_FOLDER}")
            except OSError as e:
                print(f"  ⚠️ Warning: Could not remove temporary folder {TEMP_DOWNLOAD_FOLDER}. {e}")
                
if __name__ == "__main__":
    main()