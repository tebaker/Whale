# WHALE-PUUP: Secure Package Archiver and Encoder Utility

## 1. Project Overview

WHALE-PUUP is a specialized command-line utility for the secure packaging and transport of software dependencies and project assets. It converts complex binary archives (NuGet packages or local folders) into a universally transportable Base64 encoded text format, facilitating movement across restricted environments.

## 2. Core Operational Modes

The application supports three distinct modes for archival and retrieval:

* **NuGet Archiving:** Automates the download of specified NuGet packages, archives them to ZIP, and encodes the result to Base64 TXT.
* **Folder Archiving:** Zips a local directory and converts the resulting archive into a Base64 encoded TXT file.
* **Base64 Decoding:** Reverts a Base64 TXT file back to its original binary ZIP archive format for restoration.

## 3. Building the Standalone Executable

The utility requires Python 3 and the `requests` and `pyinstaller` libraries.

The standalone executable is built using the committed `whale-puup.spec` file, which guarantees consistent configuration, including the custom icon (`icons/whale_icon.ico`).

To build, run:

```bash
pyinstaller whale-puup.spec
```

The final `whale-puup.exe` is generated within the `dist/` directory.

## 4. Repository Structure Note

The `whale-puup.spec` file is committed to the repository to ensure identical, consistent, and reproducible builds of the executable across all environments and collaborators.

                              . .,
                            '.-:-.`
                            '  :  `
                       .------ |-:,
                     .'        x   .
                    .'              .
                   .'                .
                  .'                  .
            ,     /                (o) \\----------
            \\`._/                   ,__)
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
