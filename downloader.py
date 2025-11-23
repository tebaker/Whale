# ==============================================================================
# WHALE-PUUP Downloader Module (downloader.py)
# Handles NuGet package discovery, downloading, and extraction.
# ==============================================================================

import os
import tempfile
import zipfile
import requests
import json
import utilities

# NuGet public API endpoint for package details
NUGET_API_URL = "https://api.nuget.org/v3/registration-flat/"
NUGET_PACKAGE_URL = "https://www.nuget.org/api/v2/package/"

def download_packages(package_list):
    """
    Downloads and extracts a list of NuGet packages into a temporary directory.

    Args:
        package_list (list): List of NuGet package ID strings (e.g., ['Newtonsoft.Json']).

    Returns:
        str or None: The path to the temporary directory containing extracted packages,
                     or None if any critical download fails.
    """
    
    # Create a temporary directory to hold the downloads
    temp_download_dir = tempfile.mkdtemp(prefix="whale_puup_")
    print(utilities.color(f"[DOWNLOAD] Created temporary directory: {temp_download_dir}", "YELLOW"))

    all_successful = True
    
    for package_id in package_list:
        try:
            print(utilities.color(f"\n[INFO] Processing package: {package_id}", "CYAN"))

            # 1. --- Discover Latest Version ---
            # We assume a fixed, latest version for simplicity, but a more complex
            # utility would use the registration API to find a specific version.
            # For this utility, we'll try to download without specifying version first.

            # 2. --- Construct Download URL ---
            # Nuget V2 style URL is often used for direct downloads
            download_url = f"{NUGET_PACKAGE_URL}{package_id}"
            
            # The output path for the downloaded .nupkg (which is a ZIP file)
            output_nupkg_path = os.path.join(temp_download_dir, f"{package_id}.nupkg")
            
            # 3. --- Perform Download ---
            print(utilities.color(f"[DOWNLOAD] Fetching from: {download_url}...", "YELLOW"))
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            with open(output_nupkg_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(utilities.color(f"[DOWNLOAD] Successfully saved .nupkg to: {output_nupkg_path}", "GREEN"))

            # 4. --- Extract Package ---
            extract_dir = os.path.join(temp_download_dir, package_id)
            os.makedirs(extract_dir, exist_ok=True)
            
            print(utilities.color(f"[EXTRACT] Extracting package contents...", "YELLOW"))
            
            # .nupkg files are standard ZIP archives
            with zipfile.ZipFile(output_nupkg_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(utilities.color(f"[EXTRACT] Extraction complete to: {extract_dir}", "GREEN"))

            # 5. --- Cleanup .nupkg ---
            os.remove(output_nupkg_path)
            
        except requests.exceptions.RequestException as req_e:
            print(utilities.color(f"[ERROR] Failed to download {package_id} (Network/HTTP Error): {req_e}", "RED"))
            all_successful = False
        except zipfile.BadZipFile:
            print(utilities.color(f"[ERROR] Failed to extract {package_id}: Downloaded file is corrupted or not a valid ZIP.", "RED"))
            all_successful = False
        except Exception as e:
            print(utilities.color(f"[ERROR] An unexpected error occurred while processing {package_id}: {e}", "RED"))
            all_successful = False
            
    if all_successful:
        # Return the path to the directory containing all the extracted packages
        return temp_download_dir
    else:
        # If any package failed, clean up the temp directory and return None
        utilities.cleanup(temp_download_dir)
        return None