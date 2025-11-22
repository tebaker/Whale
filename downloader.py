import subprocess

# You must have nuget.exe accessible in your system's PATH
NUGET_CMD = r'C:\Program Files (x86)\NuGet\nuget.exe'
# The base directory where all the temporary download folders reside.
TEMP_DOWNLOAD_FOLDER = "temp_downloads"

def download_nuget_packages(package_list, download_dir):
    print("Puuping:\n")

    nugetPackagesDownloaded = 0

    for package_name in package_list:
        """
        Attempts to download a single NuGet package.
        If it fails, print error and return None. Exiting the function.
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
        
        nugetPackagesDownloaded+=1
        
    # If successful, return the output (or a success indicator)
    return nugetPackagesDownloaded
