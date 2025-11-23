import json
import os
import random
import sys

def show_whale_prompt():
    """Displays a random ASCII whale from whales.json and prompts the user for packages."""
    
    # --- Part 1: Load and Display Whale ---
    
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    json_path = os.path.join(script_dir, "whales.json")
    whale_key = "fallback" # Initialize for clean output in case of error
    
    try:
        with open(json_path, 'r') as f:
            whale_config = json.load(f)
        whale_key = random.choice(list(whale_config.keys()))
        whale_ascii = "\n" + "\n".join(whale_config[whale_key])
        
    except (FileNotFoundError, Exception) as e:
        # Simplified error handling for display
        whale_ascii = "\n (~^~)\\ " 
        
    print("\n" + "="*50)
    print("Welcome to WHALE-PUUP Download Utility!")
    print(whale_ascii)
    print(f"--- Displaying the {whale_key.capitalize()} Whale ---")
    print("Please list the NuGet packages (comma-delimited) you need (type 'exit' to quit).")
    print("Example: Newtonsoft.Json, Microsoft.Extensions.Logging")
    print("="*50)

    # Initialize package_list_str to an empty string to guarantee it exists
    package_list_str = "" 

    if len(sys.argv) > 1:
        # A. Command Line Arguments: Use arguments if provided
        package_list_str = " ".join(sys.argv[1:])
        print(f"Using packages from command line: {package_list_str}\n")
    else:
        # B. Interactive Prompt: Ask the user
        package_list_str = input("🐋 Enter package name(s): ")
    
    # 1. Check for EXIT command immediately after getting the string
    if package_list_str.lower().strip() == 'exit':
        # Signal cancellation back to main()
        return None 
    
    # Split by comma, remove whitespace, filter any empty entries
    packages = [p.strip() for p in package_list_str.split(',') if p.strip()]

    # Validate for good input after split
    if not packages:
        print("\n⚠️ Input contained only separators (commas) or was empty. Please try again.")
        return None 
        
    # 4. Return the clean list of packages!
    return packages

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

# ==============================================================================
# WHALE-PUUP Utility Functions (utilities.py)
# ==============================================================================

# --- 1. Terminal Coloring Setup ---
COLOR_MAP = {
    "RED": "\033[91m", "GREEN": "\033[92m", "YELLOW": "\033[93m", 
    "BLUE": "\033[94m", "MAGENTA": "\033[95m", "CYAN": "\033[96m", 
    "ENDC": "\033[0m"
}

def color(text, color_name):
    """Wraps text in ANSI escape codes for colored terminal output."""
    return f"{COLOR_MAP.get(color_name, '')}{text}{COLOR_MAP['ENDC']}"

# --- 2. Standard Library Imports ---
import os
import sys
import shutil

def resource_path(relative_path):
    """Resolves the absolute path to a file, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def cleanup(dir_path):
    """Removes the temporary directory and all its contents recursively."""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    except Exception as e:
        print(f"[ERROR] Could not clean up temporary directory {dir_path}: {e}")

# ==============================================================================
# --- 3. Interactive Prompt Functions ---
# ==============================================================================

def prompt_for_mode():
    """
    Presents the main application menu and prompts the user for a selection.
    
    Returns:
        str or None: 'nuget', 'folder', 'decode', or None if the user chooses to exit.
    """
    print(color("\n" + "="*50, "MAGENTA"))
    print(color("🐳 WHALE-PUUP Utility: Select Operation Mode", "MAGENTA"))
    print(color("="*50, "MAGENTA"))
    print(color("  1) NuGet: Download packages, archive, and encode.", "YELLOW"))
    print(color("  2) Folder: Zip a local folder and Base64 encode it.", "YELLOW"))
    print(color("  3) Decode: Decode a Base64 TXT file back to ZIP.", "YELLOW"))
    print(color("  4) Exit", "YELLOW"))

    while True:
        choice = input("Enter selection (1, 2, 3, or 4): ").strip()
        
        if choice == '1':
            return 'nuget'
        elif choice == '2':
            return 'folder'
        elif choice == '3':
            return 'decode' # New mode
        elif choice == '4' or choice.lower() == 'exit':
            return None
        else:
            print(color("Invalid selection. Please enter 1, 2, 3, or 4.", "RED"))

def prompt_for_nuget_packages():
    """Prompts the user for a comma-separated list of NuGet package IDs."""
    print(color("\n--- NuGet Package Download Mode ---", "CYAN"))
    print(color("Enter the comma-separated list of NuGet package IDs:", "CYAN"))
    
    while True:
        packages_input = input("Packages (e.g., Newtonsoft.Json,NLog, or 'exit'): ").strip()
        
        if packages_input.lower() == 'exit':
            return None
        
        if not packages_input:
            print(color("Error: Please enter at least one package ID.", "RED"))
            continue
            
        package_list = [p.strip() for p in packages_input.split(',') if p.strip()]
        
        if not package_list:
             print(color("Error: Input contains no valid package IDs.", "RED"))
             continue
             
        return package_list

def prompt_for_source_folder():
    """Prompts the user for a directory path and validates it."""
    print(color("\n--- Folder Archiver Mode ---", "MAGENTA"))
    print(color("Enter the path to the folder you wish to ZIP and Base64 encode (e.g., C:\\MyFolder):", "CYAN"))
    
    while True:
        path = input("Folder Path (or 'exit'): ").strip()
        
        if path.lower() == 'exit':
            return None
        
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(abs_path):
            print(color(f"Error: Path not found. Please verify: {abs_path}", "RED"))
        elif not os.path.isdir(abs_path):
            print(color(f"Error: The path exists but is not a directory.", "RED"))
        else:
            print(color(f"Selected folder: {abs_path}", "GREEN"))
            return abs_path

def prompt_for_base64_file(output_base_path):
    """
    Prompts the user for the Base64 input file and the desired output ZIP filename.
    
    Args:
        output_base_path (str): The default directory to save the output ZIP.
        
    Returns:
        tuple (str, str) or None: (input_file_path, output_file_path) or None on cancellation.
    """
    print(color("\n--- Base64 Decode Mode ---", "CYAN"))
    
    # 1. Get Base64 Input File Path
    while True:
        input_path = input("Enter path to the Base64 TXT file (or 'exit'): ").strip()
        
        if input_path.lower() == 'exit':
            return None
            
        abs_input_path = os.path.abspath(os.path.expanduser(input_path))
        
        if not os.path.exists(abs_input_path):
            print(color(f"Error: Input file not found: {abs_input_path}", "RED"))
        elif not os.path.isfile(abs_input_path):
            print(color(f"Error: The path exists but is not a file.", "RED"))
        else:
            print(color(f"Base64 input file selected: {abs_input_path}", "GREEN"))
            break
            
    # 2. Get Desired Output ZIP Filename
    default_name = os.path.splitext(os.path.basename(abs_input_path))[0]
    # Remove the .base64 suffix if present to suggest a cleaner name
    if default_name.endswith(".base64"):
        default_name = default_name[:-len(".base64")]
    default_output_path = os.path.join(output_base_path, f"{default_name}_decoded.zip")
    
    print(color(f"Default output ZIP path: {default_output_path}", "YELLOW"))

    while True:
        output_name = input(f"Enter desired output ZIP filename (or press Enter for default, or 'exit'): ").strip()
        
        if output_name.lower() == 'exit':
            return None

        if not output_name:
            # Use the default path
            abs_output_path = default_output_path
        else:
            # Ensure the output has a .zip extension
            if not output_name.lower().endswith('.zip'):
                output_name += '.zip'
            
            # The output file is saved to the OUTPUT_BASE_PATH
            abs_output_path = os.path.join(output_base_path, output_name)

        print(color(f"Output ZIP will be saved to: {abs_output_path}", "GREEN"))
        return abs_input_path, abs_output_path