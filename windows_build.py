from distutils.core import setup
from py2exe.build_exe import py2exe
import os, os.path, shutil, sys

current = '1.0'

dir = 'distrib/windows'

print '[[ Running BenzinU Through py2exe! ]]'
print '>> Destination directory: %s' % dir
sys.argv.append('py2exe')

if os.path.isdir(dir): shutil.rmtree(dir)
os.makedirs(dir)

excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
			'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
			'Tkconstants', 'Tkinter', 'pdb', 'unittest', 'difflib',
			'_ssl', 'pyreadline', 'optparse', 'pickle', 'calendar']    

includes = []


packages = ['lxml.etree', 'lxml._elementpath', 'gzip']

dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'tcl84.dll',
				'tk84.dll']
setup(
    name='BenzinU',
    version=current,
    description="Converter for bflyt and bflan files",
    console=[
        {'script': 'main.py',
		"dest_base": "BenzinU"
         }
    ],
    options={'py2exe':{
        'includes': includes,
        'compressed': 1,
        'optimize': 2,
        'excludes': excludes,
		"packages": packages,
		"dll_excludes": dll_excludes,
        'bundle_files': 1,
        'dist_dir': dir
    }}
	,zipfile = None
	)

os.unlink(dir + '/w9xpopen.exe')
