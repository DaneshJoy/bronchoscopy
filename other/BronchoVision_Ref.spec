# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['BronchoVision.py'],
             pathex=['E:\\Parsiss\\Bronchoscopy_project\\Github\\bronchoscopy'],
             binaries=[],
             datas=[('ui\\icons\\exit.png', 'img'),
                     ('ui\\icons\\Open.png', 'img'),
                     ('ui\\icons\\pause.png', 'img'),
                     ('ui\\icons\\play.png', 'img'),
                     ('ui\\icons\\stop.png', 'img'),
					 ('ui\\icons\\trajectory.png', 'img'),
					 ('ui\\logo\\logo_transparent.png', 'logo')],
             hiddenimports=[],
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
		  a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
						('msvcr100.dll','C:\\Windows\\System32\\msvcr100.dll', 'BINARY')],
		  a.zipfiles,
          exclude_binaries=True,
          name='BronchoVision',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
		  icon='ui\\icons\\BronchoVision.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='BronchoVision')