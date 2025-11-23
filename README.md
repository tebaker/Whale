WHALE-PUUP: Secure Package Archiver and Encoder Utility

1. Project Overview

The WHALE-PUUP utility is a specialized command-line application designed for the secure packaging and transport of software dependencies and project assets. Its primary function is to transform binary data (such as archived NuGet packages or complex project folders) into a universally transportable Base64 encoded text format. This enables the movement of large or complex resource sets across networks or environments where standard file transfers may be restricted or unreliable.

The utility is self-contained and manages the entire workflow from source material acquisition to final encoded output, ensuring a repeatable and consistent archival process.

2. Core Operational Modes

The application operates across three distinct modes, providing flexibility for various archival and retrieval needs.

A. NuGet Archiving and Encoding (Mode 1)

This mode facilitates the automated handling of external dependencies:

Acquisition: Downloads specified packages directly from the public NuGet repository.

Archiving: Consolidates the contents of the downloaded packages into a single, structured ZIP archive.

Encoding: Converts the resulting binary ZIP file into a Base64 encoded .txt file for easy transport.

B. Local Folder Archiving and Encoding (Mode 2)

This mode is used for standard data integrity and preparation:

Archiving: Recursively compresses a specified local directory into a single ZIP archive.

Encoding: Converts the resulting binary ZIP file into a Base64 encoded .txt file.

C. Base64 Decoding (Mode 3)

This mode is used for retrieval and restoration of packages created by the utility:

Restoration: Reads an input .txt file containing the Base64 data.

Decoding: Reverts the data back to its original binary format, saving it as a functional .zip archive.

3. Getting Started

Prerequisites

To run this application, you must have Python 3 installed, along with the required libraries: requests, pyinstaller (for building the executable), and standard Python modules (os, shutil, tempfile, etc.).

Building the Standalone Executable

The recommended way to deploy the WHALE-PUUP utility is as a self-contained executable, ensuring all dependencies are bundled.

The build process is managed by the committed specification file, guaranteeing consistent results across environments.

Ensure all project files (main.py, utilities.py, archiver.py, encoder.py, downloader.py) are present.

Ensure the icon file (whale_icon.ico) is correctly placed within the icons/ subdirectory as referenced in the specification.

Execute PyInstaller, referencing the whale-puup.spec file:

pyinstaller whale-puup.spec


The final executable (whale-puup.exe) will be generated within the dist/ directory.

4. Repository Structure Note

This repository includes the whale-puup.spec file as a critical component of the source code. This practice ensures that all contributors and users can build the application identically, maintaining version consistency for the executable's configuration, bundled libraries, and metadata (such as the custom icon).
