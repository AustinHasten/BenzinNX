import os, sys, struct, webbrowser
from lxml import etree
from urllib2 import urlopen
from include import *

version = "1.0.9"

def main():
	print "BenzinU %s by Diddy81" % version

	checkupdate()
	UseMatNames, output = options()
	name, ext = os.path.splitext(sys.argv[1])
	
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close
	header = data[0:4]
	if header == "FLYT":
		bflytread = bflytRead.ReadBflyt()
		bflytread.start(data, 0, name, output, UseMatNames)
	elif header == "FLAN":
		bflanread = bflanRead.ReadBflan()
		bflanread.start(data, 0, name, output)
	else:
		try:
			tree = etree.parse(sys.argv[1])
			data = tree.getroot()
			if data.tag == "xmflyt":
				bflytwrite = bflytWrite.WriteBflyt()
				bflytwrite.start(data, name, output)
			elif data.tag == "xmflan":
				bflanwrite = bflanWrite.WriteBflan()
				bflanwrite.start(data, name, output)
			else:
				print("Unknown File Format!")
				sys.exit(1)
		except:
			e = sys.exc_info()[0]
			print( "<p>Error: %s</p>" % e )
			print("Something went wrong!")
			sys.exit(1)
			
			
def options():
	usage = """if converting bflyt/bflan to xmflyt/xmflan:
Usage: BenzinU input [option] [output]
	options:
		-m 		use Material numbers instead of names
	output:
		output file name is optional 
		
if converting xmflyt/xmflan to bflyt/bflan:
Usage: BenzinU input [output]
	output:
		output file name is optional """
	if len(sys.argv) < 2:
		print usage
		sys.exit(1)
	if len(sys.argv) >= 3:	
		if sys.argv[2].lower() == "-m":
			UseMatNames = False
			try:
				output = sys.argv[3]
			except:
				output = None				
		elif sys.argv[2].startswith("-"):
			print "Unknown option given"
			print usage
			sys.exit(1)
		else:
			UseMatNames = True
			output = sys.argv[2]
			
	elif len(sys.argv) == 2:
		try:
			output = sys.argv[2]
		except:
			output = None
		UseMatNames = True	
	else:
		print usage
		sys.exit(1)
		
	return UseMatNames, output
	
	
def checkupdate():
	contents = version
	try:
		ur = urlopen("http://pastebin.com/raw/3EHszD1v")		
		contents = ur.readline()
	except:
		pass
	if contents != version:
		update()
		
def update():
	print "A update is available for BenzinU\nWould you like to download the update now?\nSelecting Yes will end this session and open the download link"
	retCode = raw_input("Would you like to update? [y/n] ")
	if retCode.lower() == "y" or retCode.lower() == "yes":
		webbrowser.open('https://www.dropbox.com/s/bspazlngdmasckl/BenzinU.exe?dl=1', new=0, autoraise=True)
		sys.exit(1)

if __name__ == "__main__":
	main()

	