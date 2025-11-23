# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=['requests'], # Ensure requests and its dependencies are included
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='whale-puup', # This sets the output name to whale-puup.exe
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='icon/whale-icon.ico' # <--- ADDED: Path to the custom icon
          )