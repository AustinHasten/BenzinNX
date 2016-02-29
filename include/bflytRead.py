import sys, struct
from lxml import etree
from ReadTypes import Reader 
RT = Reader()
import types

class ReadBflyt(object):

	def start(self, data, pos, name, output):
		# self.setup()
		self.root = etree.Element("xmflyt")
		self.checkheader(data, pos)
		
		RT.indent(self.root)
		if output == None:
			with open(name + '.xmlyt', "w") as dirpath:
				dirpath.write(etree.tostring(self.root))
		else:
			with open(output, "w") as dirpath:
				dirpath.write(etree.tostring(self.root))
	
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
			self.pic1section(data, pos, None)
		elif magic == "txt1":
			self.txt1section(data, pos, None)
		elif magic == "wnd1":
			self.wnd1section(data, pos, None)
		elif magic == "bnd1":
			self.bnd1section(data, pos, None)
		elif magic == "prt1":
			self.prt1section(data, pos, None)
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
			print "No code for %s section at %d" %(magic, pos)
			sys.exit(1)
		
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
		lyt_offset = RT.uint16(data, pos);pos += 2	# Should be 20
		version = RT.uint16(data, pos);pos += 2 	# Always 0x0202
		pad1 = RT.uint16(data, pos);pos += 2 		# Padding
		filesize = RT.uint32(data, pos);pos += 4	# Full Filesize
		sections = RT.uint16(data, pos);pos += 2	# Number of sections
		pad2 = RT.uint16(data, pos);pos += 2 		# Padding
		self.newroot = etree.SubElement(self.root, "version", Number=str(version))
		if len(data) != filesize:
			print "BFLYT filesize doesn't match"
			sys.exit(1)
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
			FilenameOffset.append(str(RT.uint32(data, pos)));pos += 4		# read name offsets
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
			#print flags
			etree.SubElement(entries, "flags").text = str(flags)
						
			fullpos = StartPos + mat1length # debug skip section
			
			texref = RT.BitExtract(flags, 2, 30)
			TextureSRT = RT.BitExtract(flags, 2, 28)
			MappingSettings = RT.BitExtract(flags, 2, 26)
			TextureCombiners = RT.BitExtract(flags, 2, 24)
			ProjectionMapping = RT.BitExtract(flags, 2, 15)
			Indirect = RT.BitExtract(flags, 1, 17)
			AlphaTest = RT.BitExtract(flags, 1, 22)
			Blend_mode = RT.BitExtract(flags, 2, 20)
			BlendAlpha = RT.BitExtract(flags, 2, 18)
			
			# test = 30
			# while test != 0:
				# test1 = RT.BitExtract(flags, 2, test)
				# print str(test) + " has " + str(test1)
				# test -= 1
			
			loop = 0
			while loop < texref: # 4
				file = RT.uint16(data, pos);pos += 2
				wrap_s = RT.uint8(data, pos);pos += 1
				wrap_t = RT.uint8(data, pos);pos += 1
				texture = etree.SubElement(entries, "texture")
				texture.attrib['name'] = self.texturefiles[file]
				etree.SubElement(texture, "wrap_s").text = types.wraps[wrap_s]
				etree.SubElement(texture, "wrap_t").text = types.wraps[wrap_t]
				loop += 1
				
			loop = 0
			while loop < TextureSRT: # 20
				XTrans = RT.float4(data, pos);pos += 4
				YTrans = RT.float4(data, pos);pos += 4
				Rotate = RT.float4(data, pos);pos += 4
				XScale = RT.float4(data, pos);pos += 4
				YScale = RT.float4(data, pos);pos += 4
				srt = etree.SubElement(entries, "TextureSRT")
				etree.SubElement(srt, "XTrans").text = str(XTrans)
				etree.SubElement(srt, "YTrans").text = str(YTrans)
				etree.SubElement(srt, "Rotate").text = str(Rotate)
				etree.SubElement(srt, "XScale").text = str(XScale)
				etree.SubElement(srt, "YScale").text = str(YScale)
				loop += 1
			
			loop = 0
			while loop < MappingSettings: # 16
				unk = RT.uint8(data, pos);pos += 1
				MappingMethod = RT.uint8(data, pos);pos += 1
				unk2 = RT.uint8(data, pos);pos += 1
				unk3 = RT.uint8(data, pos);pos += 1
				unk4 = RT.uint8(data, pos);pos += 1
				unk5 = RT.uint8(data, pos);pos += 1
				unk6 = RT.uint8(data, pos);pos += 1
				unk7 = RT.uint8(data, pos);pos += 1
				mapping = etree.SubElement(entries, "mapping")
				etree.SubElement(mapping, "unk").text = str(unk)
				etree.SubElement(mapping, "MappingMethod").text = types.MappingTypes[MappingMethod]
				etree.SubElement(mapping, "unk2").text = str(unk2)
				etree.SubElement(mapping, "unk3").text = str(unk3)
				etree.SubElement(mapping, "unk4").text = str(unk4)
				etree.SubElement(mapping, "unk5").text = str(unk5)
				etree.SubElement(mapping, "unk6").text = str(unk6)
				etree.SubElement(mapping, "unk7").text = str(unk7)
				loop += 1
				
				
			loop = 0
			while loop < TextureCombiners: # 4
				ColorBlend = RT.uint8(data, pos);pos += 1
				AlphaBlend = RT.uint8(data, pos);pos += 1
				unk3 = RT.uint8(data, pos);pos += 1
				unk4 = RT.uint8(data, pos);pos += 1
				TexComb = etree.SubElement(entries, "TextureCombiners")
				etree.SubElement(TexComb, "ColorBlend").text = types.ColorBlendTypes[ColorBlend]
				etree.SubElement(TexComb, "AlphaBlending").text = types.BlendTypes[AlphaBlend]
				etree.SubElement(TexComb, "unk3").text = str(unk3)
				etree.SubElement(TexComb, "unk4").text = str(unk4)
				loop += 1
				
				
			loop = 0
			while loop < AlphaTest: # 
				Condition = RT.uint8(data, pos);pos += 1
				unk1 = RT.uint8(data, pos);pos += 1
				unk2 = RT.uint8(data, pos);pos += 1
				unk3 = RT.uint8(data, pos);pos += 1
				Value = RT.float4(data, pos);pos += 4
				ATest = etree.SubElement(entries, "AlphaTest")
				etree.SubElement(ATest, "Condition").text = types.AlphaTestCondition[Condition]
				etree.SubElement(ATest, "unk1").text = str(unk1)
				etree.SubElement(ATest, "unk2").text = str(unk2)
				etree.SubElement(ATest, "unk3").text = str(unk3)
				etree.SubElement(ATest, "Value").text = str(Value)			
				loop += 1
			
			loop = 0
			while loop < Blend_mode: # 
				BlendOp = RT.uint8(data, pos);pos += 1
				Src = RT.uint8(data, pos);pos += 1
				Dst = RT.uint8(data, pos);pos += 1
				LogicalOp = RT.uint8(data, pos);pos += 1
				BMode = etree.SubElement(entries, "BlendMode")
				etree.SubElement(BMode, "BlendOp").text = types.BlendCalcOp[BlendOp]
				etree.SubElement(BMode, "Src").text = types.BlendCalc[Src]
				etree.SubElement(BMode, "Dst").text = types.BlendCalc[Dst]
				etree.SubElement(BMode, "LogicalOp").text = types.LogicalCalcOp[LogicalOp]
				loop += 1
			
			loop = 0
			while loop < BlendAlpha: # 
				BlendOp = RT.uint8(data, pos);pos += 1
				Src = RT.uint8(data, pos);pos += 1
				Dst = RT.uint8(data, pos);pos += 1
				unk4 = RT.uint8(data, pos);pos += 1
				BModeA = etree.SubElement(entries, "BlendModeAlpha")
				etree.SubElement(BModeA, "BlendOp").text = types.BlendCalcOp[BlendOp]
				etree.SubElement(BModeA, "Src").text = types.BlendCalc[Src]
				etree.SubElement(BModeA, "Dst").text = types.BlendCalc[Dst]
				etree.SubElement(BModeA, "unk4").text = str(unk4)			
				loop += 1
			
			loop = 0
			while loop < Indirect: # 24
				Rotate = RT.float4(data, pos);pos += 4
				Xwarp = RT.float4(data, pos);pos += 4
				Ywarp = RT.float4(data, pos);pos += 4
				IndAdj = etree.SubElement(entries, "IndirectAdjust")
				etree.SubElement(IndAdj, "Rotate").text = str(Rotate)
				etree.SubElement(IndAdj, "Xwarp").text = str(Xwarp)
				etree.SubElement(IndAdj, "Ywarp").text = str(Ywarp)				
				loop += 1
				
			loop = 0
			while loop < ProjectionMapping: # 40
				XTrans = RT.float4(data, pos);pos += 4
				YTrans = RT.float4(data, pos);pos += 4
				XScale = RT.float4(data, pos);pos += 4
				YScale = RT.float4(data, pos);pos += 4
				option = RT.uint8(data, pos);pos += 1
				unk1 = RT.uint8(data, pos);pos += 1
				unk2 = RT.uint16(data, pos);pos += 2
				ProjectMap = etree.SubElement(entries, "ProjectionMapping")
				etree.SubElement(ProjectMap, "XTrans").text = str(XTrans)
				etree.SubElement(ProjectMap, "YTrans").text = str(YTrans)
				etree.SubElement(ProjectMap, "XScale").text = str(XScale)
				etree.SubElement(ProjectMap, "YScale").text = str(YScale)
				etree.SubElement(ProjectMap, "Option").text = types.ProjectionMappingTypes[option]
				etree.SubElement(ProjectMap, "unk1").text = str(unk1)
				etree.SubElement(ProjectMap, "unk2").text = str(unk2)
				loop += 1
				
			i += 1
		#-------------------------------------------------------------------------------------------------
		
		# fullpos = StartPos + mat1length # debug skip section
		# print "fullpos = %d" %fullpos
		# print "real pos = %d" %pos
		
		self.checkheader(data, pos)	
		
	def panesection(self, data, pos, tag): 
		flags = RT.uint8(data, pos);pos += 1
		origin = RT.uint8(data, pos);pos += 1
		alpha = RT.uint8(data, pos);pos += 1
		partscale = RT.uint8(data, pos);pos += 1
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
		mainorigin = origin%16
		parentorigin = origin/16
		
		tag.attrib['name'] = name	
		etree.SubElement(tag, "visible").text = str(flags & 1)
		etree.SubElement(tag, "TransmitAlpha2Children").text = str((flags & 2) >>1)
		etree.SubElement(tag, "PositionAdjustment").text = str((flags & 4) >>2)
		originTree = etree.SubElement(tag, "origin")
		originTree.attrib['x'] = types.originX[mainorigin%4]
		originTree.attrib['y'] = types.originY[mainorigin/4]
		originTree = etree.SubElement(tag, "OriginOfParent")
		originTree.attrib['x'] = types.originX[parentorigin%4]
		originTree.attrib['y'] = types.originY[parentorigin/4]
		etree.SubElement(tag, "alpha").text = str(alpha)
		etree.SubElement(tag, "PartScaling").text = str(partscale)
		translateTree = etree.SubElement(tag, "translate")
		etree.SubElement(translateTree, "x").text = "%.18f" %XTrans
		etree.SubElement(translateTree, "y").text = "%.18f" %YTrans
		etree.SubElement(translateTree, "z").text = "%.18f" %ZTrans
		rotateTree = etree.SubElement(tag, "rotate")
		etree.SubElement(rotateTree, "x").text = "%.18f" %XRotate
		etree.SubElement(rotateTree, "y").text = "%.18f" %YRotate
		etree.SubElement(rotateTree, "z").text = "%.18f" %ZRotate
		scaleTree = etree.SubElement(tag, "scale")
		etree.SubElement(scaleTree, "x").text = "%.18f" %XScale
		etree.SubElement(scaleTree, "y").text = "%.18f" %YScale
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
		
	def pic1section(self, data, pos, prt):
		StartPos = pos
		pic1magic, pic1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		if prt == None:
			tag = etree.SubElement(self.newroot, "tag", type="pic1")
		else:
			tag = etree.SubElement(prt, "tag", type="pic1")
			
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
		
		if prt == None:
			self.checkheader(data, pos)
		else:
			return
				
	def txt1section(self, data, pos, prt):
		StartPos = pos
		txt1magic, txt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		if prt == None:
			tag = etree.SubElement(self.newroot, "tag", type="txt1")
		else:
			tag = etree.SubElement(prt, "tag", type="txt1")
		
		pos = self.panesection(data, pos, tag)								# read pane info 84
		len1 = RT.uint16(data, pos);pos += 2
		len2 = RT.uint16(data, pos);pos += 2
		mat_num = RT.uint16(data, pos);pos += 2
		font_idx = RT.uint16(data, pos);pos += 2
		alignment = RT.uint8(data, pos);pos += 1
		LineAlignment = RT.uint8(data, pos);pos += 1
		unk = RT.uint16(data, pos);pos += 2
		name_offs = RT.uint32(data, pos);pos += 4
		StartOfTextOffset = RT.uint32(data, pos);pos += 4
		color1 = RT.uint32(data, pos);pos += 4
		color2 = RT.uint32(data, pos);pos += 4
		font_size_x = RT.float4(data, pos);pos += 4
		font_size_y = RT.float4(data, pos);pos += 4
		char_space = RT.float4(data, pos);pos += 4
		line_space = RT.float4(data, pos);pos += 4
		callnameoffset = RT.uint32(data, pos);pos += 4
		unkfloat = RT.float4(data, pos);pos += 4
		unkfloat1 = RT.float4(data, pos);pos += 4
		unkfloat2 = RT.float4(data, pos);pos += 4
		unkfloat3 = RT.float4(data, pos);pos += 4
		unkcolor1 = RT.uint32(data, pos);pos += 4
		unkcolor2 = RT.uint32(data, pos);pos += 4
		unk2 = RT.uint32(data, pos);pos += 4
		
		
		
		etree.SubElement(tag, "length").text = str(len2)
		etree.SubElement(tag, "restrictlength").text = str(len1)
		etree.SubElement(tag, "material", name = self.MaterialNames[mat_num])
		font = etree.SubElement(tag, "font", index=str(font_idx))
		originTree = etree.SubElement(font, "alignment")
		originTree.attrib['x'] = str(alignment%3)	
		originTree.attrib['y'] = str(alignment/3)	
		etree.SubElement(font, "LineAlignment").text = str(LineAlignment)
		etree.SubElement(font, "unk").text = str(unk)
		etree.SubElement(font, "name_offs").text = str(name_offs)
		# etree.SubElement(font, "OffsetStartOfText").text = str(StartOfTextOffset)
		topcolor = etree.SubElement(tag, "topcolor")
		topcolor.attrib['R'] = str(color1 >> 24)
		topcolor.attrib['G'] = str(color1 >> 16 & 0xff)
		topcolor.attrib['B'] = str(color1 >> 8 & 0xff)
		topcolor.attrib['A'] = str(color1 >> 0 & 0xff)
		bottomcolor = etree.SubElement(tag, "bottomcolor")
		bottomcolor.attrib['R'] = str(color2 >> 24)
		bottomcolor.attrib['G'] = str(color2 >> 16 & 0xff)
		bottomcolor.attrib['B'] = str(color2 >> 8 & 0xff)
		bottomcolor.attrib['A'] = str(color2 >> 0 & 0xff)
		etree.SubElement(font, "xsize").text = str(font_size_x)
		etree.SubElement(font, "ysize").text = str(font_size_y)
		etree.SubElement(font, "charsize").text = str(char_space)
		etree.SubElement(font, "linesize").text = str(line_space)
		# etree.SubElement(font, "callnameoffset").text = str(callnameoffset)
		new = etree.SubElement(tag, "newstuff")
		etree.SubElement(new, "unkfloat").text = "%.18f" %unkfloat
		etree.SubElement(new, "unkfloat1").text = "%.18f" %unkfloat1
		etree.SubElement(new, "unkfloat2").text = "%.18f" %unkfloat2
		etree.SubElement(new, "unkfloat3").text = "%.18f" %unkfloat3
		unkcolor1tree = etree.SubElement(new, "unkcolor1")
		unkcolor1tree.attrib['R'] = str(unkcolor1 >> 24)
		unkcolor1tree.attrib['G'] = str(unkcolor1 >> 16 & 0xff)
		unkcolor1tree.attrib['B'] = str(unkcolor1 >> 8 & 0xff)
		unkcolor1tree.attrib['A'] = str(unkcolor1 >> 0 & 0xff)
		unkcolor2tree = etree.SubElement(new, "unkcolor2")
		unkcolor2tree.attrib['R'] = str(unkcolor2 >> 24)
		unkcolor2tree.attrib['G'] = str(unkcolor2 >> 16 & 0xff)
		unkcolor2tree.attrib['B'] = str(unkcolor2 >> 8 & 0xff)
		unkcolor2tree.attrib['A'] = str(unkcolor2 >> 0 & 0xff)
		etree.SubElement(new, "unk2").text = str(unk2)
		etree.SubElement(tag, "text").text = data[pos:pos + len2].encode("hex");pos += RT.by4(len2)
		callname = RT.getstr(data[pos:]);pos += RT.by4(int(len(callname)) +1)
		etree.SubElement(tag, "callname").text = callname
		
		
		
		
		fullpos = StartPos + txt1length # debug skip section		
		etree.SubElement(tag, "dump").text = data[pos:fullpos].encode("hex")
		if prt == None:
			self.checkheader(data, fullpos)
		else:
			return
		
	def wnd1section(self, data, pos, prt):
		StartPos = pos
		wnd1magic, wnd1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		fullpos = StartPos + wnd1length
		
		if prt == None:
			tag = etree.SubElement(self.newroot, "tag", type="wnd1")
		else:
			tag = etree.SubElement(prt, "tag", type="wnd1")
		pos = self.panesection(data, pos, tag)								# read pane info
		wndd = etree.SubElement(tag, "wnd")
		for i in xrange(4):
			etree.SubElement(wndd, "coordinate").text = str(RT.float4(data, pos));pos += 4
			
		FrameCount = RT.uint8(data, pos);pos += 1
		etree.SubElement(wndd, "FrameCount").text = str(FrameCount)
		etree.SubElement(wndd, "unk1").text = str(RT.uint8(data, pos));pos += 1
		pad = RT.uint16(data, pos);pos += 2
		offset1 = str(RT.uint32(data, pos));pos += 4
		offset2 = str(RT.uint32(data, pos));pos += 4
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
				
		wnd4offset = []
		for i in xrange(FrameCount):
			wnd4offset.append(str(RT.uint32(data, pos)));pos += 4
		wndmat = etree.SubElement(tag, "wnd4mat")
		for i in xrange(FrameCount):
			etree.SubElement(wndmat, "material").text = self.MaterialNames[RT.uint16(data, pos)];pos += 2
			etree.SubElement(wndmat, "index").text = str(RT.uint8(data, pos));pos += 1
			pad2 = RT.uint8(data, pos);pos += 1
		
		if pos != fullpos:
			etree.SubElement(tag, "dump").text = data[pos:fullpos].encode("hex")
			pos = fullpos
		
		if prt == None:
			self.checkheader(data, pos)
		else:
			return
		
	def bnd1section(self, data, pos, prt):
		StartPos = pos
		bnd1magic, bnd1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		if prt == None:
			tag = etree.SubElement(self.newroot, "tag", type="bnd1")
		else:
			tag = etree.SubElement(prt, "tag", type="bnd1")
		pos = self.panesection(data, pos, tag)								# read pane info
		
		pos = StartPos + bnd1length # debug skip section
		
		if prt == None:
			self.checkheader(data, pos)
		else:
			return
		
	def prt1section(self, data, pos, prt):
		StartPos = pos
		prt1magic, prt1length, pos = self.ReadMagic(data,pos)				# read magic & section length
		
		if prt == None:
			tag = etree.SubElement(self.newroot, "tag", type="prt1")
		else:
			tag = etree.SubElement(prt, "tag", type="prt1")
		pos = self.panesection(data, pos, tag)								# read pane info
		section = etree.SubElement(tag, "section")
		count = RT.uint32(data, pos);pos += 4
		unkfloat1 = RT.float4(data, pos);pos += 4
		unkfloat2 = RT.float4(data, pos);pos += 4
		unkfloat = etree.SubElement(section, "unkfloat")
		unkfloat.attrib['x'] = str(unkfloat1)
		unkfloat.attrib['y'] = str(unkfloat2)
		sectionsizes = 0
		extradatacount = 0
		i = 0
		while i < count:
			entryname = RT.getstr(data[pos:]);pos += 24
			unk1 = RT.uint8(data, pos);pos += 1
			unk2 = RT.uint8(data, pos);pos += 1
			pad1 = RT.uint16(data, pos);pos += 2
			entryoffset = RT.uint32(data, pos);pos += 4
			pad2 = RT.uint32(data, pos);pos += 4
			extraoffset = RT.uint32(data, pos);pos += 4
			
			entry = etree.SubElement(section, "entry")
			entry.attrib['entryname'] = entryname
			etree.SubElement(entry, "unk1").text = str(unk1)
			etree.SubElement(entry, "unk2").text = str(unk2)
			
			 
			if entryoffset > 0:
				temppos = StartPos + entryoffset
				magic = data[temppos:temppos + 4]
				sectionsizes += RT.uint32(data, temppos + 4)
				if magic == "pic1":
					self.pic1section(data, temppos, entry)
				elif magic == "txt1":
					self.txt1section(data, temppos, entry)
				elif magic == "wnd1":
					self.wnd1section(data, temppos, entry)
				elif magic == "bnd1":
					self.bnd1section(data, temppos, entry)
				elif magic == "prt1":
					self.prt1section(data, temppos, entry)
				
			if extraoffset > 0:
				temppos = StartPos + extraoffset
				etree.SubElement(entry, "extradata").text = data[temppos:temppos + 48].encode("hex")
				extradatacount += 1
				
			
			i += 1
		
		name = RT.getstr(data[pos:]);pos += RT.by4(len(name) + 1)
		section.attrib['name'] = name
		
		
		pos += sectionsizes
		pos += 48 * extradatacount
		if prt == None:
			self.checkheader(data, pos)
		else:
			return
		
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
			
		checkpos = StartPos + grp1length
		if checkpos != pos:
			toread = checkpos - pos
			etree.SubElement(tag, "dump").text = data[pos:checkpos].encode("hex")
			pos += toread
		
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
		try:
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
					
		except:
			etree.SubElement(tag, "dump").text = data[StartPos+8:StartPos+cnt1length].encode("hex")
	
		fullpos = StartPos + cnt1length # debug skip section		
		self.checkheader(data, fullpos)		
			
	def debugfile(self, data):
		
		with open("data.bin", "w") as dirpath:
			dirpath.write(data)