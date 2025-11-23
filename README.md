# WHALE-PUUP: Secure Package Archiver and Encoder Utility
                            . ..
                           '.-:-.`
                           '  :  `
                       .----- |-:.
                     .'        x   .
                    .'              .
                   .'                .
                  .'                  .
            ,     /                (⚙︎) \----------.
            \`._/                    ,__)          | 
      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~      ⚓︎
## 1. Project Overview
* **NuGet Archiving:** Automates download of specified NuGet packages, archives them to ZIP, encodes them to Base64.
* **Folder Archiving:** Zips and converts a folder into Base64.
* **Base64 Decoding:** Decodes Base64 to original ZIP.

## 3. Building the Standalone Executable

The utility requires Python 3 and the `requests` and `pyinstaller` libraries.
Built using the committed `whale-puup.spec` file, which guarantees consistent configuration, including the custom icon (`icons/whale_icon.ico`).

To build, run:
```bash
pyinstaller whale-puup.spec
```
The final `whale-puup.exe` is generated within the `dist/` directory.

## 4. Repository Structure Note
The `whale-puup.spec` file is committed to the repository to ensure identical, consistent, and reproducible builds of the executable across all environments and collaborators.
