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
			FilenameOffset.append(str(RT.uint32(data, pos)));pos += 4		# read name offsets
			loop += 1
		startoftexlist = pos
		tag = etree.SubElement(self.newroot, "tag", type="txl1")
		entries = etree.SubElement(tag, "entries")
		self.texturefiles = []
		for i in xrange(len(FilenameOffset)):
			Filenames = RT.getstr(data[pos:]);pos += int(len(Filenames)+1)	# read the names
			self.texturefiles.append(Filenames)
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
		SizeHeader = RT.uint16(data, pos);pos += 2							# Offset to list start. Always zero
		
		tag = etree.SubElement(self.newroot, "tag", type="mat1")
		
		MaterialOffset = []
		while len(MaterialOffset) < NumMaterials:
			MaterialOffset.append(RT.uint32(data, pos));pos += 4
		self.MaterialNames = []
		i = 0
		while i < NumMaterials:
			MatName = RT.getstr(data[pos:]);pos += 28
			self.MaterialNames.append(MatName)
			entries = etree.SubElement(tag, "entries", name=MatName)
			colors = etree.SubElement(entries, "colors" )
			fore_color = []
			while len(fore_color) < 4:
				fore_color.append(RT.uint8(data, pos));pos += 1
			colorfore = etree.SubElement(colors, "forecolor")
			colorfore.attrib['R'] = str(fore_color[0])
			colorfore.attrib['G'] = str(fore_color[1])
			colorfore.attrib['B'] = str(fore_color[2])
			colorfore.attrib['A'] = str(fore_color[3])
			back_color = []
			while len(back_color) < 4:
				back_color.append(RT.uint8(data, pos));pos += 1
			colorback = etree.SubElement(colors, "backcolor")
			colorback.attrib['R'] = str(back_color[0])
			colorback.attrib['G'] = str(back_color[1])
			colorback.attrib['B'] = str(back_color[2])
			colorback.attrib['A'] = str(back_color[3])
			flags = RT.uint32(data, pos);pos += 4
			etree.SubElement(entries, "flags").text = str(flags)
			
			
			texref = RT.BitExtract(flags, 2, 28)
			TextureSRT = RT.BitExtract(flags, 3, 27)
			print "%s has %d"%(MatName, TextureSRT)
			
			
			# loop = 0
			# while loop < texref:
				# file = RT.uint16(data, pos);pos += 2
				# wrap_s = RT.uint8(data, pos);pos += 1
				# wrap_t = RT.uint8(data, pos);pos += 1
				# texture = etree.SubElement(entries, "texture")
				# texture.attrib['name'] = self.texturefiles[file]
				# etree.SubElement(texture, "wrap_s").text = str(wrap_s)
				# etree.SubElement(texture, "wrap_t").text = str(wrap_t)
				# loop += 1
				
			if flags == 21:
				etree.SubElement(entries, "dump").text = data[pos:pos+32].encode("hex")
				pos += 32
			elif flags == 1130:
				etree.SubElement(entries, "dump").text = data[pos:pos+72].encode("hex")
				pos += 72
			elif flags == 533:
				etree.SubElement(entries, "dump").text = data[pos:pos+40].encode("hex")
				pos += 40
			elif flags == 131072:
				etree.SubElement(entries, "dump").text = data[pos:pos+8].encode("hex")
				pos += 8
			elif flags == 703:
				etree.SubElement(entries, "dump").text = data[pos:pos+112].encode("hex")
				pos += 112
			elif flags == 1215:
				etree.SubElement(entries, "dump").text = data[pos:pos+108].encode("hex")
				pos += 108
		
		
			i += 1
		#-------------------------------------------------------------------------------------------------
		
		fullpos = StartPos + mat1length # debug skip section		
		
		self.checkheader(data, fullpos)	
		
	def panesection(self, data, pos, tag):
		flags = RT.uint8(data, pos);pos += 1
		origin = RT.uint8(data, pos);pos += 1
		alpha = RT.uint8(data, pos);pos += 1
		unk = RT.uint8(data, pos);pos += 1
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
		etree.SubElement(tag, "unk").text = str(unk)
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
		vtxColorTL = RT.uint32(data, pos);pos += 4
		vtxColorTR = RT.uint32(data, pos);pos += 4
		vtxColorBL = RT.uint32(data, pos);pos += 4
		vtxColorBR = RT.uint32(data, pos);pos += 4
		mat_num = RT.uint16(data, pos);pos += 2
		num_texcoords = RT.uint8(data, pos);pos += 1
		pad = RT.uint8(data, pos);pos += 1
		etree.SubElement(tag, "material").text = self.MaterialNames[mat_num]
		colors = etree.SubElement(tag, "colors")
		vtxColTL = etree.SubElement(colors, "vtxColorTL")
		vtxColTL.attrib['R'] = str(vtxColorTL >> 24)
		vtxColTL.attrib['G'] = str(vtxColorTL >> 16 & 0xff)
		vtxColTL.attrib['B'] = str(vtxColorTL >> 8 & 0xff)
		vtxColTL.attrib['A'] = str(vtxColorTL >> 0 & 0xff)
		vtxColTR = etree.SubElement(colors, "vtxColorTR")
		vtxColTR.attrib['R'] = str(vtxColorTR >> 24)
		vtxColTR.attrib['G'] = str(vtxColorTR >> 16 & 0xff)
		vtxColTR.attrib['B'] = str(vtxColorTR >> 8 & 0xff)
		vtxColTR.attrib['A'] = str(vtxColorTR >> 0 & 0xff)
		vtxColBL = etree.SubElement(colors, "vtxColorBL")
		vtxColBL.attrib['R'] = str(vtxColorBL >> 24)
		vtxColBL.attrib['G'] = str(vtxColorBL >> 16 & 0xff)
		vtxColBL.attrib['B'] = str(vtxColorBL >> 8 & 0xff)
		vtxColBL.attrib['A'] = str(vtxColorBL >> 0 & 0xff)
		vtxColBR = etree.SubElement(colors, "vtxColorBR")
		vtxColBR.attrib['R'] = str(vtxColorBR >> 24)
		vtxColBR.attrib['G'] = str(vtxColorBR >> 16 & 0xff)
		vtxColBR.attrib['B'] = str(vtxColorBR >> 8 & 0xff)
		vtxColBR.attrib['A'] = str(vtxColorBR >> 0 & 0xff)
		coordinates = etree.SubElement(tag, "coordinates")
		i = 0
		while i < num_texcoords:
			set = etree.SubElement(coordinates, "set")
			coord = etree.SubElement(set, "coordTL")
			coord.attrib['s'] = str(RT.float4(data, pos));pos += 4
			coord.attrib['t'] = str(RT.float4(data, pos));pos += 4
			coord = etree.SubElement(set, "coordTR")
			coord.attrib['s'] = str(RT.float4(data, pos));pos += 4
			coord.attrib['t'] = str(RT.float4(data, pos));pos += 4
			coord = etree.SubElement(set, "coordBL")
			coord.attrib['s'] = str(RT.float4(data, pos));pos += 4
			coord.attrib['t'] = str(RT.float4(data, pos));pos += 4
			coord = etree.SubElement(set, "coordBR")
			coord.attrib['s'] = str(RT.float4(data, pos));pos += 4
			coord.attrib['t'] = str(RT.float4(data, pos));pos += 4
			i += 1
		
		self.checkheader(data, pos)	
		
	def txt1section(self, data, pos):
		StartPos = pos
		txt1magic, txt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="txt1")
		pos = self.panesection(data, pos, tag)								# read pane info
		# len1 = RT.uint16(data, pos);pos += 2
		# len2 = RT.uint16(data, pos);pos += 2
		# mat_num = RT.uint16(data, pos);pos += 2
		# font_idx = RT.uint16(data, pos);pos += 2
		# alignment = RT.uint8(data, pos);pos += 1
		# unk_char = RT.uint8(data, pos);pos += 1
		# pad = RT.uint16(data, pos);pos += 2
		# name_offs = RT.uint32(data, pos);pos += 4
		# color1 = RT.uint32(data, pos);pos += 4
		# color2 = RT.uint32(data, pos);pos += 4
		# font_size_x = RT.float4(data, pos);pos += 4
		# font_size_y = RT.float4(data, pos);pos += 4
		# char_space = RT.float4(data, pos);pos += 4
		# line_space = RT.float4(data, pos);pos += 4
		
		
		fullpos = StartPos + txt1length # debug skip section		
		etree.SubElement(tag, "dump").text = data[pos:fullpos].encode("hex")
		self.checkheader(data, fullpos)		
		
	def wnd1section(self, data, pos):
		StartPos = pos
		wnd1magic, wnd1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		tag = etree.SubElement(self.newroot, "tag", type="wnd1")
		pos = self.panesection(data, pos, tag)								# read pane info
		wndd = etree.SubElement(tag, "wnd")
		for i in xrange(4):
			etree.SubElement(wndd, "coordinate").text = str(RT.float4(data, pos));pos += 4
			
		etree.SubElement(wndd, "FrameCount").text = str(RT.uint8(data, pos));pos += 1
		etree.SubElement(wndd, "unk1").text = str(RT.uint8(data, pos));pos += 1
		pad = RT.uint16(data, pos);pos += 2
		etree.SubElement(wndd, "offset1").text = str(RT.uint32(data, pos));pos += 4
		etree.SubElement(wndd, "offset2").text = str(RT.uint32(data, pos));pos += 4
		wnddd = etree.SubElement(tag, "wnd1")
		for i in xrange(4):
			color =etree.SubElement(wnddd, "color")
			color.attrib["R"] = str(RT.uint8(data, pos));pos += 1
			color.attrib["G"] = str(RT.uint8(data, pos));pos += 1
			color.attrib["B"] = str(RT.uint8(data, pos));pos += 1
			color.attrib["A"] = str(RT.uint8(data, pos));pos += 1
			
		etree.SubElement(wnddd, "material").text = self.MaterialNames[RT.uint16(data, pos)];pos += 2
		coordinate_count = RT.uint8(data, pos);pos += 1
		etree.SubElement(wnddd, "coordinate_count").text = str(coordinate_count)
		pad1 = RT.uint8(data, pos);pos += 1
		if coordinate_count != 0:
			wnddddd = etree.SubElement(tag, "Coords")
			for i in xrange(coordinate_count):
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				etree.SubElement(wnddddd, "texcoord").text = str(RT.float4(data, pos));pos += 4
				
		wndddddd = etree.SubElement(tag, "wnd4")
		etree.SubElement(wndddddd, "offset").text = str(RT.uint32(data, pos));pos += 4
		wndmat = etree.SubElement(tag, "wnd4mat")
		etree.SubElement(wndmat, "material").text = self.MaterialNames[RT.uint16(data, pos)];pos += 2
		etree.SubElement(wndmat, "index").text = str(RT.uint8(data, pos));pos += 1
		pad2 = RT.uint8(data, pos);pos += 1
				
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
		
		
		fullpos = StartPos + prt1length # debug skip section		
		etree.SubElement(tag, "dump").text = data[pos:fullpos].encode("hex")
		self.checkheader(data, fullpos)		
		
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
		firstoffset = RT.uint32(data, pos);pos += 4
		firstcount = RT.uint16(data, pos);pos += 2
		secondcount = RT.uint16(data, pos);pos += 2
		name = RT.getstr(data[pos:])
		tag.attrib['name'] = name		
		if firstoffset > 0:
			pos = StartPos + firstoffset
			i = 0
			while i < firstcount:
				etree.SubElement(tag, "first").text = RT.getstr(data[pos:]);pos += 24
				i += 1
							
		if secondcount > 0:
			entrypos = pos
			secondoffsets = []
			i = 0
			while i < secondcount:
				secondoffsets.append(RT.uint32(data, pos));pos += 4
				i+=1
			for j in secondoffsets:
				pos = entrypos + j
				etree.SubElement(tag, "second").text = RT.getstr(data[pos:])
		
		
		
		fullpos = StartPos + cnt1length # debug skip section		
		self.checkheader(data, fullpos)		
		
		
		
	def debugfile(self, data):
		
		with open("data.bin", "w") as dirpath:
			dirpath.write(data)