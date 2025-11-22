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
