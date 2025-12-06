import sys
import os
import shutil
import archiver
import utilities
import downloader
import encoder 

# --- Configuration ---
OUTPUT_BASE_PATH = os.path.join(os.getcwd(), "final_archives")

def run_success_message(source_path, zip_path, base64_path=None):
    """Prints the final success message with paths. Generalized for decode mode."""
    print("\n" + utilities.color("="*50, "GREEN"))
    print(utilities.color("🎉 WHALE-PUUP Operation Complete!", "GREEN"))
    
    if base64_path and zip_path:
        # Encoding/Archiving success message
        print(utilities.color(f"Source Path Processed: {source_path}", "GREEN")) 
        print(utilities.color(f"ZIP Archive created: {zip_path}", "GREEN"))
        print(utilities.color(f"Base64 Encoded TXT: {base64_path}", "GREEN"))
    elif source_path and zip_path:
        # Decoding success message (source_path is the base64 input file)
        print(utilities.color(f"Base64 Input File: {source_path}", "GREEN"))
        print(utilities.color(f"Decoded Output ZIP: {zip_path}", "GREEN"))
    
    print(utilities.color("="*50, "GREEN"))

def run_nuget_mode():
    """Handles the full NuGet download, archive, and encode workflow."""
    
    download_dir = None
    
    try:
        # 1. --- GET INPUT: Prompt for package names ---
        packages = utilities.prompt_for_nuget_packages()
        
        if packages is None:
            print(utilities.color("NuGet process cancelled. Returning to menu.", "RED"))
            return
            
        os.makedirs(OUTPUT_BASE_PATH, exist_ok=True)
            
        print(utilities.color("\nAll puup'd out. Now digesting NuGet packages...", "CYAN"))

        # 2. --- DOWNLOAD & EXTRACT PACKAGES ---
        # The corrected call: download_packages now creates and returns the directory path.
        download_dir = downloader.download_packages(packages)

        if not download_dir:
            raise Exception("NuGet download or extraction failed.")
        
        if zip_path is None or base64_output_path is None:
            raise Exception("Archiving and encoding failed.")

        # 4. --- SUCCESS MESSAGE ---
        run_success_message(download_dir, zip_path, base64_output_path)
        
    except Exception as e:
        print(utilities.color(f"\n⚠️ A CRITICAL error occurred during NuGet mode: {e}", "RED"))
        
    finally:
        # 5. --- CLEANUP ---
        if download_dir and os.path.exists(download_dir):
            utilities.cleanup(download_dir)
            print(utilities.color(f"\n🗑️ Cleaned up temporary folder: {download_dir}", "YELLOW"))


def run_folder_mode():
    """Handles the local folder zip and Base64 encode workflow."""
    
    source_folder_path = None
    
    try:
        # 1. --- GET INPUT: Prompt for the folder path ---
        source_folder_path = utilities.prompt_for_source_folder()
        
        if source_folder_path is None:
            print(utilities.color("Folder mode cancelled. Returning to menu.", "RED"))
            return
            
        os.makedirs(OUTPUT_BASE_PATH, exist_ok=True)
            
        print(utilities.color("\nAll puup'd out. Now digesting local folder...", "CYAN"))

        # 2. --- ARCHIVE AND ENCODE ---
        zip_path, base64_output_path = archiver.archive_and_encode_packages(
            source_dir=source_folder_path,
            dest_folder=OUTPUT_BASE_PATH
        )
        
        if zip_path is None or base64_output_path is None:
            raise Exception("Archiving and encoding failed.")

        # 3. --- SUCCESS MESSAGE ---
        run_success_message(source_folder_path, zip_path, base64_output_path)
        
    except Exception as e:
        print(utilities.color(f"\n⚠️ A CRITICAL error occurred during Folder mode: {e}", "RED"))

def run_decode_mode():
    """Handles decoding a Base64 TXT file back to a binary ZIP file."""
    
    input_path = None
    output_path = None
    
    try:
        # 1. --- GET INPUT: Prompt for the Base64 TXT file and output name ---
        os.makedirs(OUTPUT_BASE_PATH, exist_ok=True)
        paths = utilities.prompt_for_base64_file(OUTPUT_BASE_PATH)
        
        if paths is None:
            print(utilities.color("Decode process cancelled. Returning to menu.", "RED"))
            return
            
        input_path, output_path = paths

        print(utilities.color("\nStarting Base64 decoding...", "CYAN"))

        # 2. --- DECODE ---
        success = encoder.decode_file_from_base64(input_path, output_path)
        
        if not success:
            raise Exception("Base64 decoding failed.")

        # 3. --- SUCCESS MESSAGE ---
        run_success_message(input_path, output_path, base64_path=None) 

    except Exception as e:
        print(utilities.color(f"\n⚠️ A CRITICAL error occurred during Decode mode: {e}", "RED"))
        
        # Cleanup partially written output file if it exists and failed
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
                print(utilities.color(f"\n🗑️ Cleaned up failed output file: {output_path}", "YELLOW"))
            except OSError:
                pass


def main():
    """
    Main loop to present the user with a choice of operation modes.
    """
    while True:
        mode = utilities.prompt_for_mode()
        
        if mode == 'nuget':
            run_nuget_mode()
        elif mode == 'folder':
            run_folder_mode()
        elif mode == 'decode':
            run_decode_mode()
        elif mode is None:
            print(utilities.color("\nExiting WHALE-PUUP. Goodbye!", "MAGENTA"))
            sys.exit(0)
            
if __name__ == "__main__":
    main()