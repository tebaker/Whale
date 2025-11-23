import sys
import os
import shutil
# Make sure to import the new encoder function
from encoder import encode_file_to_base64
# Import from local modules
from downloader import download_nuget_packages, TEMP_DOWNLOAD_FOLDER, NUGET_CMD
from archiver import extract_nupkg_packages, create_zip_archive
from utilities import show_whale_prompt

# --- Configuration ---
OUTPUT_BASE_PATH = "final_archives"

def main():
    """Main method to orchestrate the entire process."""
    
    source_folder_path = None
    final_zip_path = None # Initialize for use in cleanup/reporting
    
    try:
        # 1. --- GET INPUT ---
        # Note: We must use a variable that holds the list of packages, not the raw string
        packages = show_whale_prompt() 
        
        if packages is None:
            print("\nProcess canceled or no valid packages entered. Exiting.")
            sys.exit(0)
            
        # 2. --- DOWNLOAD ---
        downloaded_count = download_nuget_packages(packages, TEMP_DOWNLOAD_FOLDER)
            
        if downloaded_count == 0:
            print("\n❌ No packages were successfully downloaded. Exiting with error.")
            sys.exit(1)
            
        print("\nAll puup'd out. Now digesting...")

        # 3. --- EXTRACT & ARCHIVE ---
        
        # NOTE: extract_nupkg_packages MUST return the absolute path to the output folder.
        source_folder_path = extract_nupkg_packages()

        if source_folder_path is None:
            # Crucial check: if extraction failed, we must stop here.
            raise Exception("Extraction failed: could not determine final source folder path.")

        # Create archive zip and place it *inside* the source folder
        final_zip_path = create_zip_archive(source_folder_path)
        
        if final_zip_path is None:
             raise Exception("Archiving failed: ZIP file was not created.")

        # 4. --- BASE64 ENCODING (The new step!) ---
        
        # Define the output path for the Base64 file (.txt extension for email compatibility)
        # 🛠️ FIX: Use os.path.splitext to strip the existing .zip extension before adding .txt
        base_name_no_ext = os.path.splitext(final_zip_path)[0]
        base64_output_path = base_name_no_ext + ".txt"
        
        # Call the new function, ensuring we pass ONLY the final ZIP path
        encode_file_to_base64(final_zip_path, base64_output_path)
    
        # 5. --- SUCCESS MESSAGE ---
        print("\n\n" + "="*50)
        print("🎉 WHALE-PUUP Operation Complete!")
        print(f"Final output folder: {source_folder_path}")
        print(f"ZIP archive: {final_zip_path}")
        print(f"Base64 encoded file: {base64_output_path}") # This now shows the .txt extension
        print("="*50)
        
    except Exception as e:
        # Catch any unexpected errors during the process
        print(f"\n⚠️ A CRITICAL and unexpected error occurred: {e}")
        print("Please check your input and configuration files.")
        sys.exit(1)

    finally:
        # 6. --- CLEANUP ---
        if os.path.exists(TEMP_DOWNLOAD_FOLDER):
            try:
                shutil.rmtree(TEMP_DOWNLOAD_FOLDER)
                print(f"\n🗑️ Cleaned up temporary folder: {TEMP_DOWNLOAD_FOLDER}")
            except OSError as e:
                print(f"  ⚠️ Warning: Could not remove temporary folder {TEMP_DOWNLOAD_FOLDER}. {e}")
                
if __name__ == "__main__":
    main()