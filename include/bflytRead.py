import sys, struct
from lxml import etree
from ReadTypes import Reader 
# import ReadTypes as RT
RT = Reader()

class ReadBflyt(object):

	def start(self, data, pos, name):
		self.root = etree.Element("xmflyt")
		self.checkheader(data, pos)
		
		#RT.indent(self.root)
		with open(name + '.xml', "w") as dirpath:
			dirpath.write(etree.tostring(self.root, pretty_print=True))
	
	def checkheader(self, data, pos):
		magic = data[pos:pos + 4]
		if magic == "FLYT":
			self.bflytHeader(data, pos)
		elif magic == "lyt1":
			self.lyt1section(data, pos)
		elif magic == "txl1":
			self.txl1section(data, pos)
		elif magic == "fnl1":
			self.fnl1section(data, pos)
		elif magic == "mat1":
			self.mat1section(data, pos)
		elif magic == "pan1":
			self.pan1section(data, pos)
		elif magic == "pas1":
			self.pas1section(data, pos)
		elif magic == "pic1":
			self.pic1section(data, pos)
		elif magic == "txt1":
			self.txt1section(data, pos)
		elif magic == "wnd1":
			self.wnd1section(data, pos)
		elif magic == "bnd1":
			self.bnd1section(data, pos)
		elif magic == "prt1":
			self.prt1section(data, pos)
		elif magic == "pae1":
			self.pae1section(data, pos)
		elif magic == "grp1":
			self.grp1section(data, pos)
		elif magic == "grs1":
			self.grs1section(data, pos)
		elif magic == "gre1":
			self.gre1section(data, pos)
		elif magic == "cnt1":
			self.cnt1section(data, pos)
		elif len(data) == pos:
			print "Done"			
		else:
			print "No code for %s section at %s" %(magic, hex(pos))
			#sys.exit(1)
		
	def ReadMagic(self, data, pos):
		magic = data[pos:pos + 4]; pos += 4
		seclength = RT.uint32(data, pos);pos += 4
		return magic,seclength,pos
		
	def bflytHeader(self, data, pos):
		bflytmagic = data[0:4]; pos += 4
		endian = RT.uint16(data, pos);pos += 2
		if endian == 65279: #0xFEFF - Big Endian
			pass
		else:
			print("Little endian not supported!")
			sys.exit(1)
		lyt_offsetree = RT.uint16(data, pos);pos += 2	# Should be 20
		version = RT.uint16(data, pos);pos += 2 	# Always 0x0202
		pad1 = RT.uint16(data, pos);pos += 2 		# Padding
		filesize = RT.uint32(data, pos);pos += 4	# Full Filesize
		sections = RT.uint16(data, pos);pos += 2	# Number of sections
		pad2 = RT.uint16(data, pos);pos += 2 		# Padding
		self.newroot = etree.SubElement(self.root, "version", Number=str(version))
		self.checkheader(data, pos)	
		
	def lyt1section(self, data, pos):
		lyt1magic, lyt1length, pos = self.ReadMagic(data,pos)			# read magic & section length
		drawnFromMiddle = RT.uint8(data, pos);pos += 1					# drawn from middle of the screen
		pad = RT.uint24(data, pos);pos += 3								# padding 0x000000
		width = RT.float4(data, pos);pos += 4							# screen width
		height = RT.float4(data, pos);pos += 4							# screen height
		unk1 = RT.float4(data, pos);pos += 4							# unknown value
		unk2 = RT.float4(data, pos);pos += 4							# unknown seems to be the same as unk1
		filename = RT.getstr(data[pos:]);pos += RT.by4(int(len(filename)) + 1)	# looks to be the filename
		tag = etree.SubElement(self.newroot, "tag", type="lyt1")
		etree.SubElement(tag, "drawnFromMiddle").text = str(drawnFromMiddle)
		etree.SubElement(tag, "width").text = str(width)
		etree.SubElement(tag, "height").text = str(height)
		etree.SubElement(tag, "unk1").text = str(unk1)
		etree.SubElement(tag, "unk2").text = str(unk2)
		etree.SubElement(tag, "filename").text = str(filename)
		self.checkheader(data, pos)	
		#self.debugfile(filename)
				
	def fnl1section(self, data, pos):
		fnl1magic, fnl1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		NumFonts = RT.uint16(data, pos);pos += 2							# number of textures in section
		OffsetToNextSection = RT.uint16(data, pos);pos += 2					# Should be 0
		loop = 0
		FilenameOffset = []
		while loop < NumFonts:
			FilenameOffset.append(str(RT.uint32(data, pos)));pos += 4		# read name offsetrees
			loop += 1
		startoffontlist = pos
		tag = etree.SubElement(self.newroot, "tag", type="fnl1")
		entries = etree.SubElement(tag, "entries")
		for i in xrange(len(FilenameOffset)):
			Filenames = RT.getstr(data[pos:]);pos += int(len(Filenames)+1)	# read the names
			etree.SubElement(entries, "name").text = Filenames
		
		endoffontlist = pos
		padd = endoffontlist - startoffontlist
		pad = RT.by4(padd) - padd
		pos += pad
		self.checkheader(data, pos)	
	
	def txl1section(self, data, pos):
		txl1magic, txl1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		NumTextures = RT.uint16(data, pos);pos += 2							# number of textures in section
		OffsetToNextSection = RT.uint16(data, pos);pos += 2					# Should be 0
		loop = 0
		FilenameOffset = []
		while loop < NumTextures:
			FilenameOffset.append(str(RT.uint32(data, pos)));pos += 4		# read name offsetrees
			loop += 1
		startoftexlist = pos
		tag = etree.SubElement(self.newroot, "tag", type="txl1")
		entries = etree.SubElement(tag, "entries")
		for i in xrange(len(FilenameOffset)):
			Filenames = RT.getstr(data[pos:]);pos += int(len(Filenames)+1)	# read the names
			etree.SubElement(entries, "name").text = Filenames
		
		endoftexlist = pos
		padd = endoftexlist - startoftexlist
		pad = RT.by4(padd) - padd
		pos += pad
		self.checkheader(data, pos)	
			
	def mat1section(self, data, pos):
		StartPos = pos
		mat1magic, mat1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		NumMaterials = RT.uint16(data, pos);pos += 2						# number of materials in section
		SizeHeader = RT.uint16(data, pos);pos += 2							# Offsetree to list start. Always zero
		
		tag = etree.SubElement(self.newroot, "tag", type="mat1")
		
		pos = StartPos + mat1length # debug skip section
		# MaterialOffsetree = []
		# while len(MaterialOffsetree) < NumMaterials:
			# MaterialOffsetree.append(RT.uint32(data, pos));pos += 4
			
		# i = 0
		# while i < NumMaterials:
		# MatName = RT.getstr(data[pos:]);pos += 28		
		# entries = etree.SubElement(tag, "entries", name=MatName)
		# colors = etree.SubElement(entries, "colors" )
		# fore_color = []
		# while len(fore_color) < 4:
			# fore_color.append(RT.uint8(data, pos));pos += 1
		# colorfore = etree.SubElement(colors, "forecolor")
		# colorfore.attrib['R'] = str(fore_color[0])
		# colorfore.attrib['G'] = str(fore_color[1])
		# colorfore.attrib['B'] = str(fore_color[2])
		# colorfore.attrib['A'] = str(fore_color[3])
		# back_color = []
		# while len(back_color) < 4:
			# back_color.append(RT.uint8(data, pos));pos += 1
		# colorback = etree.SubElement(colors, "backcolor")
		# colorback.attrib['R'] = str(back_color[0])
		# colorback.attrib['G'] = str(back_color[1])
		# colorback.attrib['B'] = str(back_color[2])
		# colorback.attrib['A'] = str(back_color[3])
		# colorReg3 = []
		# while len(colorReg3) < 4:
			# colorReg3.append(RT.uint8(data, pos));pos += 1
		# reg3color = etree.SubElement(colors, "colorReg3")
		# reg3color.attrib['R'] = str(colorReg3[0])
		# reg3color.attrib['G'] = str(colorReg3[1])
		# reg3color.attrib['B'] = str(colorReg3[2])
		# reg3color.attrib['A'] = str(colorReg3[3])
		# tev_k1 = []
		# while len(tev_k1) < 4:
			# tev_k1.append(RT.uint8(data, pos));pos += 1
		# k1tev = etree.SubElement(colors, "tev_k1")
		# k1tev.attrib['R'] = str(tev_k1[0])
		# k1tev.attrib['G'] = str(tev_k1[1])
		# k1tev.attrib['B'] = str(tev_k1[2])
		# k1tev.attrib['A'] = str(tev_k1[3])
		# tev_k2 = []
		# while len(tev_k2) < 4:
			# tev_k2.append(RT.uint8(data, pos));pos += 1
		# k2tev = etree.SubElement(colors, "tev_k2")
		# k2tev.attrib['R'] = str(tev_k2[0])
		# k2tev.attrib['G'] = str(tev_k2[1])
		# k2tev.attrib['B'] = str(tev_k2[2])
		# k2tev.attrib['A'] = str(tev_k2[3])
		# tev_k3 = []
		# while len(tev_k3) < 4:
			# tev_k3.append(RT.uint8(data, pos));pos += 1
		# k3tev = etree.SubElement(colors, "tev_k3")
		# k3tev.attrib['R'] = str(tev_k3[0])
		# k3tev.attrib['G'] = str(tev_k3[1])
		# k3tev.attrib['B'] = str(tev_k3[2])
		# k3tev.attrib['A'] = str(tev_k3[3])
		# tev_k4 = []
		# while len(tev_k4) < 4:
			# tev_k4.append(RT.uint8(data, pos));pos += 1
		# k4tev = etree.SubElement(colors, "tev_k4")
		# k4tev.attrib['R'] = str(tev_k4[0])
		# k4tev.attrib['G'] = str(tev_k4[1])
		# k4tev.attrib['B'] = str(tev_k4[2])
		# k4tev.attrib['A'] = str(tev_k4[3])
		
		
		
		# i += 1
		#-------------------------------------------------------------------------------------------------
		
		#print hex(pos)
		self.checkheader(data, pos)	
		
	def panesection(self, data, pos, tag):
		flags = RT.uint8(data, pos);pos += 1
		origin = RT.uint8(data, pos);pos += 1
		alpha = RT.uint8(data, pos);pos += 1
		pad = RT.uint8(data, pos);pos += 1
		name = RT.getstr(data[pos:]);pos += 32
		XTrans = RT.float4(data, pos);pos += 4
		YTrans = RT.float4(data, pos);pos += 4
		ZTrans = RT.float4(data, pos);pos += 4
		XRotate = RT.float4(data, pos);pos += 4
		YRotate = RT.float4(data, pos);pos += 4
		ZRotate = RT.float4(data, pos);pos += 4
		XScale = RT.float4(data, pos);pos += 4
		YScale = RT.float4(data, pos);pos += 4
		width = RT.float4(data, pos);pos += 4
		height = RT.float4(data, pos);pos += 4
		tag.attrib['name'] = name	
		etree.SubElement(tag, "visible").text = str(flags & 1)
		etree.SubElement(tag, "WidescreenAffected").text = str((flags & 2) >>1)		# Not sure if this is still needed
		etree.SubElement(tag, "flag").text = str((flags & 4) >>2)
		originTree = etree.SubElement(tag, "origin")
		originTree.attrib['x'] = str(origin%3)	
		originTree.attrib['y'] = str(origin/3)	
		etree.SubElement(tag, "alpha").text = str(alpha)
		translateTree = etree.SubElement(tag, "translate")
		etree.SubElement(translateTree, "x").text = str(XTrans)
		etree.SubElement(translateTree, "y").text = str(YTrans)
		etree.SubElement(translateTree, "z").text = str(ZTrans)
		rotateTree = etree.SubElement(tag, "rotate")
		etree.SubElement(rotateTree, "x").text = str(XRotate)
		etree.SubElement(rotateTree, "y").text = str(YRotate)
		etree.SubElement(rotateTree, "z").text = str(ZRotate)
		scaleTree = etree.SubElement(tag, "scale")
		etree.SubElement(scaleTree, "x").text = str(XScale)
		etree.SubElement(scaleTree, "y").text = str(YScale)
		sizeTree = etree.SubElement(tag, "size")
		etree.SubElement(sizeTree, "x").text = str(width)
		etree.SubElement(sizeTree, "y").text = str(height)
		return pos
	
	def pan1section(self, data, pos):
		StartPos = pos
		pan1magic, pan1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="pan1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		self.checkheader(data, pos)	
		
	def pas1section(self, data, pos):
		StartPos = pos
		pas1magic, pas1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="pas1")
		
		
		self.checkheader(data, pos)	
		
	def pic1section(self, data, pos):
		StartPos = pos
		pic1magic, pic1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="pic1")
		pos = self.panesection(data, pos, tag)								# read pane info
		pos = StartPos + pic1length # debug skip section
		self.checkheader(data, pos)	
		
	def txt1section(self, data, pos):
		StartPos = pos
		txt1magic, txt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="txt1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		pos = StartPos + txt1length # debug skip section
		self.checkheader(data, pos)			
		
	def wnd1section(self, data, pos):
		StartPos = pos
		wnd1magic, wnd1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="wnd1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		pos = StartPos + wnd1length # debug skip section
		self.checkheader(data, pos)	
		
	def bnd1section(self, data, pos):
		StartPos = pos
		bnd1magic, bnd1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="bnd1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		pos = StartPos + bnd1length # debug skip section
		self.checkheader(data, pos)	
		
	def prt1section(self, data, pos):
		StartPos = pos
		prt1magic, prt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="prt1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		pos = StartPos + prt1length # debug skip section
		self.checkheader(data, pos)	
		
	def pae1section(self, data, pos):
		StartPos = pos
		pae1magic, pae1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="pae1")
		
		pos = StartPos + pae1length # debug skip section
		self.checkheader(data, pos)	
		
	def grp1section(self, data, pos):
		StartPos = pos
		grp1magic, grp1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="grp1")
		GroupName = RT.getstr(data[pos:]);pos += 24
		numsubs = RT.uint16(data, pos);pos += 2
		unk = RT.uint16(data, pos);pos += 2
		tag.attrib['name'] = GroupName
		if numsubs > 0:
			subs = etree.SubElement(tag, "subs")
			
		i = 0
		while i < numsubs:
			etree.SubElement(subs, "sub").text = RT.getstr(data[pos:]);pos += 24
			i += 1
		
		
		self.checkheader(data, pos)	
		
	def grs1section(self, data, pos):
		StartPos = pos
		grs1magic, grs1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="grs1")
		
		pos = StartPos + grs1length # debug skip section
		self.checkheader(data, pos)	
		
	def gre1section(self, data, pos):
		StartPos = pos
		gre1magic, gre1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="gre1")
		
		pos = StartPos + gre1length # debug skip section
		self.checkheader(data, pos)	
				
	def cnt1section(self, data, pos):
		StartPos = pos
		cnt1magic, cnt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="cnt1")
		
		pos = StartPos + cnt1length # debug skip section
		self.checkheader(data, pos)	
		
		
		
		
	
	
	
	
	
	
	def debugfile(self, data):
		
		with open("data.bin", "w") as dirpath:
			dirpath.write(data)
			
			