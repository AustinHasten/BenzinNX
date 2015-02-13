import os, sys, struct
import xml.etree.ElementTree as ET
from include import *

def main():
	if len(sys.argv) != 2:
		print("Usage: Main file.x")
		sys.exit(1)
		
	name, ext = os.path.splitext(sys.argv[1])
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close
	header = data[0:4]
	if header == "FLYT":
		bflytread = bflytRead.ReadBflyt()
		bflytread.start(data, 0, name)
	else:
		# try:
		tree = ET.parse(sys.argv[1])
		data = tree.getroot()
		if data.tag == "xmflyt":
			bflytwrite = bflytWrite.WriteBflyt()
			bflytwrite.start(data, name)
		# except:
			# e = sys.exc_info()[0]
			# print( "<p>Error: %s</p>" % e )
			# print("Unknown File Format!")
			# sys.exit(1)

if __name__ == "__main__":
	main()
