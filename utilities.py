import os

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
