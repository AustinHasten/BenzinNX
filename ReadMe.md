# This is dead. If you're interested in customizing the home menu, I'd suggest reaching out to Team Qcean.

# BenzinNX

A fork of BenzinU by Diddy81, meant to process files used by the Nintendo Switch rather than the Nintendo WiiU. Very much a work in progress.

Things that do work:

    Converting .bflan files to .xmlan files (100% success rate on my 5.1.0 files)
    Converting .xmlan files to .bflan files (Unless the file contains an FLEU section)

Not tested:

    Packing converted .bflan files into .szs files and using with LayeredFS.

Things that I plan to do:

    Fix converting .xmlan files to .bflan files when the file contains an FLEU section

Things that I may or may not do:

    Add .bflyt/.xmlyt conversion.

BenzinU ReadMe below.

WIP python based benzin for the new bflyt format in the wii U layout files

Usage: BenzinU input [option] [output]
	options:
		-m 		use Material numbers instead of names
	output:
		output file name is optional 
		
if converting xmflyt/xmflan to bflyt/bflan:
Usage: BenzinU input [output]
	output:
		output file name is optional """

file can be a bflyt or the xml program checks compatibility before converting file 

Dependencies:-
lxml
py2exe for building

Build :-
Use python 2.7 and run the windows_build.py
