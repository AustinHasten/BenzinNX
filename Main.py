import os, sys, struct
from lxml import etree
from include import *

def main():
	if len(sys.argv) < 2:
		print("Usage: BenzinU input [output]")
		sys.exit(1)
		
	name, ext = os.path.splitext(sys.argv[1])
	try:
		output = sys.argv[2]
	except:
		output = None
	f = open(sys.argv[1], "rb")
	data = f.read()
	f.close
	header = data[0:4]
	if header == "FLYT":
		bflytread = bflytRead.ReadBflyt()
		bflytread.start(data, 0, name, output)
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
		except:
			e = sys.exc_info()[0]
			print( "<p>Error: %s</p>" % e )
			print("Unknown File Format!")
			sys.exit(1)

if __name__ == "__main__":
	main()
