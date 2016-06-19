import struct, sys, traceback
from WriteTypes import Writer 
import binascii
WT = Writer()
import types

class WriteBflyt(object):

	bflytVersion = 0

	def start(self, data, name, output):
		self.FileSections = 0
		self.texturefiles = []
		self.fontfiles = []
		self.OutFile = ""
		self.version = data.find("version")
		self.bflytVersion = int(self.version.get("Number"))
		
		tags = self.version.findall("tag")		
		for i in tags:
			#print i.get('type')
			if i.get('type') == "lyt1":
				self.OutFile += self.writelyt1(i)
				self.FileSections += 1
			elif i.get('type') == "txl1":
				self.OutFile += self.writetxl1(i)
				self.FileSections += 1
			elif i.get('type') == "fnl1":
				self.OutFile += self.writefnl1(i)
				self.FileSections += 1
			elif i.get('type') == "mat1":
				self.OutFile += self.writemat1(i)
				self.FileSections += 1
			elif i.get('type') == "pan1":
				self.OutFile += self.writepan1(i)
				self.FileSections += 1
			elif i.get('type') == "pas1":
				self.OutFile += self.writepas1(i)
				self.FileSections += 1
			elif i.get('type') == "pic1":
				self.OutFile += self.writepic1(i)
				self.FileSections += 1
			elif i.get('type') == "bnd1":
				self.OutFile += self.writepan1(i)
				self.FileSections += 1
			elif i.get('type') == "wnd1":
				self.OutFile += self.writewnd1(i)
				self.FileSections += 1
			elif i.get('type') == "txt1":
				self.OutFile += self.writetxt1(i)
				self.FileSections += 1
			elif i.get('type') == "prt1":
				self.OutFile += self.writeprt1(i)
				self.FileSections += 1
			elif i.get('type') == "usd1":
				self.OutFile += self.writeusd1(i)
				self.FileSections += 1
			elif i.get('type') == "pae1":
				self.OutFile += self.writepas1(i)
				self.FileSections += 1
			elif i.get('type') == "grp1":
				self.OutFile += self.writegrp1(i)
				self.FileSections += 1
			elif i.get('type') == "grs1":
				self.OutFile += self.writepas1(i)
				self.FileSections += 1
			elif i.get('type') == "gre1":
				self.OutFile += self.writepas1(i)
				self.FileSections += 1
			elif i.get('type') == "cnt1":
				self.OutFile += self.writecnt1(i)
				self.FileSections += 1
		
		self.OutFile = self.header() + self.OutFile
		try:
			if output == None:
				with open(name + '.bflyt', "wb") as dirpath:
					dirpath.write(self.OutFile)
			else:
				with open(output, "wb") as dirpath:
					dirpath.write(self.OutFile)
			print "File Converted"
		except:
			print "Destination file is in use"
		
		
	def header(self):
		return struct.pack(">4s4HI2H","FLYT",65279,20,self.bflytVersion,0,int(len(self.OutFile)) + 20,self.FileSections,0)
			
	def writelyt1(self, sec):
		try:
			drawnFromMiddle = int(sec.find("drawnFromMiddle").text)		
			pad = 0
			width = float(sec.find("width").text)
			height = float(sec.find("height").text)
			MaxPartsWidth = float(sec.find("MaxPartsWidth").text)
			MaxPartsHeight = float(sec.find("MaxPartsHeight").text)
			filename = sec.find("filename").text
			TempSec = struct.pack(">4b4f%ds"%WT.by4(len(filename)),drawnFromMiddle,pad,pad,pad,width,height,MaxPartsWidth,MaxPartsHeight,filename)
			lyt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
			lyt1sec += TempSec
			return lyt1sec
		except AttributeError:			
			print "%s missing from lyt1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
		
	def writetxl1(self, sec):
		temp = sec.find("entries")
		data = list(temp)
		NumTextures = len(data)
		FilenameOffset = [4*len(data)]
		names = struct.pack(">%ds"%WT.plusnull(len(data[0].text)),data[0].text)
		self.texturefiles.append(data[0].text)
		
		i = 1
		while i < len(data):
			self.texturefiles.append(data[i].text)
			FilenameOffset.append(len(names) + FilenameOffset[0])
			temp = struct.pack(">%ds"%WT.plusnull(len(data[i].text)),data[i].text)
			names += temp
			i += 1
			
		while len(names) % 4 != 0:
			names += "\x00"
		
		TempSec = struct.pack('>%sI' % len(FilenameOffset), *FilenameOffset)
		
		TempSec += names
		txl1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec))+12,NumTextures,0)
		txl1sec += TempSec
		return txl1sec
		
	def writefnl1(self, sec):
		temp = sec.find("entries")
		data = list(temp)
		Numfonts = len(data)
		FilenameOffset = [4*len(data)]
		names = struct.pack(">%ds"%WT.plusnull(len(data[0].text)),data[0].text)
		self.fontfiles.append(data[0].text)
		
		i = 1
		while i < len(data):
			self.fontfiles.append(data[i].text)
			FilenameOffset.append(len(names) + FilenameOffset[0])
			temp = struct.pack(">%ds"%WT.plusnull(len(data[i].text)),data[i].text)
			names += temp
			i += 1
			
		while len(names) % 4 != 0:
			names += "\x00"
		
		TempSec = struct.pack('>%sI' % len(FilenameOffset), *FilenameOffset)
		
		TempSec += names
		fnl1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec))+12,Numfonts,0)
		fnl1sec += TempSec
		return fnl1sec
		
	def writemat1(self, sec):
		try:
			temp = sec.findall("entries")
			self.MatList = []
			MatOffset = [4*len(temp)+12]
			for i in temp:
				name = i.get("name")
				self.MatList.append(name)
				temp2 = i.find("colors")
				temp3 = temp2.find("forecolor")
				forecolR = temp3.get("R")
				forecolG = temp3.get("G")
				forecolB = temp3.get("B")
				forecolA = temp3.get("A")
				temp3 = temp2.find("backcolor")
				backcolR = temp3.get("R")
				backcolG = temp3.get("G")
				backcolB = temp3.get("B")
				backcolA = temp3.get("A")
				#flags = i.find("flags").text
				TempSec = ""
				flags = 0
										
				texref = i.findall("texture")
				if i.find("texture") != None:
					for loop in texref:
						flags += WT.BitInsert(1,1,2,30)
						try:
							file = self.texturefiles.index(loop.get("name"))
						except ValueError:
							print "%s texture file not found in txl1" %loop.get("name")
							sys.exit(1)
							
						
						wrap_s = WT.RepresentsInt(loop.find("wrap_s").text, types.wraps)
						wrap_t = WT.RepresentsInt(loop.find("wrap_t").text, types.wraps)
						TempSec += struct.pack(">H2B", file, wrap_s, wrap_t)
				
				TextureSRT = i.findall("TextureSRT")
				if i.find("TextureSRT") != None:
					for loop in TextureSRT:
						flags += WT.BitInsert(1,1,2,28)
						XTrans = float(loop.find("XTrans").text)
						YTrans = float(loop.find("YTrans").text)
						Rotate = float(loop.find("Rotate").text)
						XScale = float(loop.find("XScale").text)
						YScale = float(loop.find("YScale").text)
						TempSec += struct.pack(">5f", XTrans, YTrans, Rotate, XScale, YScale)
						
						
				mapping = i.findall("mapping")
				if i.find("mapping") != None:
					for loop in mapping:
						flags += WT.BitInsert(1,1,2,26)
						unk = int(loop.find("unk").text)
						MappingMethod = WT.RepresentsInt(loop.find("MappingMethod").text, types.MappingTypes)
						unk2 = int(loop.find("unk2").text)
						unk3 = int(loop.find("unk3").text)
						unk4 = int(loop.find("unk4").text)
						unk5 = int(loop.find("unk5").text)
						unk6 = int(loop.find("unk6").text)
						unk7 = int(loop.find("unk7").text)
						TempSec += struct.pack(">8B", unk, MappingMethod, unk2, unk3, unk4, unk5, unk6, unk7)
						
						
				TextureCombiners = i.findall("TextureCombiners")
				if i.find("TextureCombiners") != None:
					for loop in TextureCombiners:
						flags += WT.BitInsert(1,1,2,24)
						ColorBlend = WT.RepresentsInt(loop.find("ColorBlend").text, types.ColorBlendTypes)
						AlphaBlending = WT.RepresentsInt(loop.find("AlphaBlending").text, types.BlendTypes)
						unk3 = int(loop.find("unk3").text)
						unk4 = int(loop.find("unk4").text)
						TempSec += struct.pack(">4B", ColorBlend, AlphaBlending, unk3, unk4)
						
				AlphaTest = i.findall("AlphaTest")
				if i.find("AlphaTest") != None:
					for loop in AlphaTest:
						flags += WT.BitInsert(1,1,1,22)
						Condition = WT.RepresentsInt(loop.find("Condition").text, types.AlphaTestCondition)
						unk1 = int(loop.find("unk1").text)
						unk2 = int(loop.find("unk2").text)
						unk3 = int(loop.find("unk3").text)
						Value = float(loop.find("Value").text)
						TempSec += struct.pack(">4Bf", Condition, unk1, unk2, unk3, Value)
						
				BlendMode = i.findall("BlendMode")
				if i.find("BlendMode") != None:
					for loop in BlendMode:
						flags += WT.BitInsert(1,1,2,20)
						BlendOp = WT.RepresentsInt(loop.find("BlendOp").text, types.BlendCalcOp)
						Src = WT.RepresentsInt(loop.find("Src").text, types.BlendCalc)
						Dst = WT.RepresentsInt(loop.find("Dst").text, types.BlendCalc)
						LogicalOp = WT.RepresentsInt(loop.find("LogicalOp").text, types.LogicalCalcOp)
						TempSec += struct.pack(">4B", BlendOp, Src, Dst, LogicalOp)
						
				BlendModeAlpha = i.findall("BlendModeAlpha")
				if i.find("BlendModeAlpha") != None:
					for loop in BlendModeAlpha:
						flags += WT.BitInsert(1,1,2,18)
						BlendOp = WT.RepresentsInt(loop.find("BlendOp").text, types.BlendCalcOp)
						Src = WT.RepresentsInt(loop.find("Src").text, types.BlendCalc)
						Dst = WT.RepresentsInt(loop.find("Dst").text, types.BlendCalc)
						unk4 = int(loop.find("unk4").text)
						TempSec += struct.pack(">4B", BlendOp, Src, Dst, unk4)
						
				Indirect = i.findall("IndirectAdjust")
				if i.find("IndirectAdjust") != None:
					for loop in Indirect:
						flags += WT.BitInsert(1,1,1,17)
						Rotate = float(loop.find("Rotate").text)
						Xwarp = float(loop.find("Xwarp").text)
						Ywarp = float(loop.find("Ywarp").text)
						TempSec += struct.pack(">3f", Rotate, Xwarp, Ywarp)
						
				ProjectionMapping = i.findall("ProjectionMapping")
				if i.find("ProjectionMapping") != None:
					for loop in ProjectionMapping:
						flags += WT.BitInsert(1,1,2,15)
						XTrans = float(loop.find("XTrans").text)
						YTrans = float(loop.find("YTrans").text)
						XScale = float(loop.find("XScale").text)
						YScale = float(loop.find("YScale").text)
						Option = WT.RepresentsInt(loop.find("Option").text, types.ProjectionMappingTypes)
						unk1 = int(loop.find("unk1").text)
						unk2 = int(loop.find("unk2").text)
						TempSec += struct.pack(">4f2BH", XTrans, YTrans, XScale, YScale, Option, unk1, unk2)
						
						
				ShadowBlending = i.findall("ShadowBlending")
				if i.find("ShadowBlending") != None:
					for loop in ShadowBlending:
						flags += WT.BitInsert(1,1,1,14)
						temp2 = loop.find("BlackBlending")
						BlackcolR = temp2.get("R")
						BlackcolG = temp2.get("G")
						BlackcolB = temp2.get("B")
						temp2 = loop.find("WhiteBlending")
						WhitecolR = temp2.get("R")
						WhitecolG = temp2.get("G")
						WhitecolB = temp2.get("B")
						WhitecolA = temp2.get("A")
						pad = loop.find("padding").text
						TempSec += struct.pack(">8B",int(BlackcolR),int(BlackcolG),int(BlackcolB),
											int(WhitecolR),int(WhitecolG),int(WhitecolB),int(WhitecolA),int(pad))
						
						
				# if int(flags) != 0:
					# TempSec += binascii.unhexlify(i.find("dump").text)
				if len(MatOffset) < len(temp):
					MatOffset.append(MatOffset[-1] + len(TempSec))
					
				fullTempSec = struct.pack(">28s8BI",name,int(forecolR),int(forecolG),int(forecolB),int(forecolA),
										int(backcolR),int(backcolG),int(backcolB),int(backcolA),int(flags))
				fullTempSec += TempSec
				
			TempSec2 = struct.pack('>%sI' % len(MatOffset), *MatOffset)
			TempSec2 += fullTempSec
			mat1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec2))+12,len(temp),0)
			mat1sec += TempSec2
			return mat1sec
		except AttributeError:			
			print "%s missing from mat1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
				
	def writepan1(self, sec):
		TempSec = self.writepaneinfo(sec)
		pan1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		pan1sec += TempSec		
		return pan1sec
				
	def writepas1(self, sec):
		pas1sec = struct.pack(">4sI",sec.get('type'),8)	
		return pas1sec
		
	def writepic1(self, sec):
		try:
			TempSec = self.writepaneinfo(sec)
			temp = sec.find("colors")
			temp2 = temp.find("vtxColorTL")
			vtxColorTL = int(temp2.get("R")) << 24
			vtxColorTL |= int(temp2.get("G")) << 16
			vtxColorTL |= int(temp2.get("B")) << 8
			vtxColorTL |= int(temp2.get("A")) 
			temp2 = temp.find("vtxColorTR")
			vtxColorTR = int(temp2.get("R")) << 24
			vtxColorTR |= int(temp2.get("G")) << 16
			vtxColorTR |= int(temp2.get("B")) << 8
			vtxColorTR |= int(temp2.get("A")) 
			temp2 = temp.find("vtxColorBL")
			vtxColorBL = int(temp2.get("R")) << 24
			vtxColorBL |= int(temp2.get("G")) << 16
			vtxColorBL |= int(temp2.get("B")) << 8
			vtxColorBL |= int(temp2.get("A")) 
			temp2 = temp.find("vtxColorBR")
			vtxColorBR = int(temp2.get("R")) << 24
			vtxColorBR |= int(temp2.get("G")) << 16
			vtxColorBR |= int(temp2.get("B")) << 8
			vtxColorBR |= int(temp2.get("A")) 
			mat_num = self.MatErr(sec.find("material").text)
			temp = sec.find("coordinates")
			num_texcoords = temp.findall('set')
			texcoords = ""
			for set in num_texcoords:
				coordTL_s = float(set.find("coordTL").get("s"))
				coordTL_t = float(set.find("coordTL").get("t"))
				coordTR_s = float(set.find("coordTR").get("s"))
				coordTR_t = float(set.find("coordTR").get("t"))
				coordBL_s = float(set.find("coordBL").get("s"))
				coordBL_t = float(set.find("coordBL").get("t"))
				coordBR_s = float(set.find("coordBR").get("s"))
				coordBR_t = float(set.find("coordBR").get("t"))
				texcoords += struct.pack(">8f", coordTL_s, coordTL_t, coordTR_s, coordTR_t, coordBL_s, coordBL_t, coordBR_s, coordBR_t)
			
			
			TempSec += struct.pack(">4IH2B", vtxColorTL, vtxColorTR, vtxColorBL, vtxColorBR, mat_num, len(num_texcoords), 0)
			TempSec += texcoords
			pic1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
			pic1sec += TempSec				
			return pic1sec
		except AttributeError:			
			print "%s missing from pic1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
	
	def writewnd1(self, sec):
		try:
			TempSec = self.writepaneinfo(sec)
			wnd = sec.find("wnd")
			stretchLeft = int(wnd.find("stretchLeft").text)
			stretchRight = int(wnd.find("stretchRight").text)
			stretchUp = int(wnd.find("stretchUp").text)
			stretchDown = int(wnd.find("stretchDown").text)
			customLeft = int(wnd.find("customLeft").text)
			customRight = int(wnd.find("customRight").text)
			customUp = int(wnd.find("customUp").text)
			customDown = int(wnd.find("customDown").text)
			
			FrameCount = int(wnd.find("FrameCount").text)
			unk1 = int(wnd.find("flags").text)
			# offset1 = int(wnd.find("offset1").text)
			# offset2 = int(wnd.find("offset2").text)
			wnd1 = sec.find("wnd1")
			color = wnd1.findall("color")
			material = self.MatErr(wnd1.find("material").text)
			coordinate_count = int(wnd1.find("coordinate_count").text)
			offset2 = 132 + 32 * coordinate_count
			coordSec = ""
			if coordinate_count > 0:
				Coords = sec.findall("Coords")
				for each in Coords:
					texcoordSec = each.findall("texcoord")
					texcoords = []
					for i in texcoordSec:
						texcoords.append(float(i.text))
					
					coordSec += struct.pack('>%sf' % len(texcoords), *texcoords)
					
			# wnd4  = sec.find("wnd4")
			# offset = wnd4.findall("offset")
			wnd4mat = sec.find("wnd4mat")		
			wnd4matmat = wnd4mat.findall("material")
			indexlist = wnd4mat.findall("index")
			part1 = struct.pack('>8H4B2I16BH2B', stretchLeft, stretchRight, stretchUp, stretchDown, customLeft, customRight, customUp, customDown,
								FrameCount, unk1, 0, 0, 112, offset2,
								int(color[0].get("R")), int(color[0].get("G")), int(color[0].get("B")), int(color[0].get("A")),
								int(color[1].get("R")), int(color[1].get("G")), int(color[1].get("B")), int(color[1].get("A")),
								int(color[2].get("R")), int(color[2].get("G")), int(color[2].get("B")), int(color[2].get("A")),
								int(color[3].get("R")), int(color[3].get("G")), int(color[3].get("B")), int(color[3].get("A")),
								material, coordinate_count, 0
								)
			offset = len(TempSec) + len(part1) + len(coordSec) + 8
			part2 = struct.pack('>I', offset + 4 * len(wnd4matmat))
			part3 = struct.pack(">H2B",self.MatErr(wnd4matmat[0].text),int(indexlist[0].text),0)
			wnd4matmaterial = []
			i = 1
			while i < len(wnd4matmat):
				part2 += struct.pack('>I', offset + 4 * len(wnd4matmat) + 4 * i)
				part3 += struct.pack(">H2B",self.MatErr(wnd4matmat[i].text),int(indexlist[i].text),0)
				index = int(indexlist[i].text)
				i += 1
			
			
			TempSec += part1
			TempSec += coordSec
			TempSec += part2
			TempSec += part3
			wnd1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
			wnd1sec += TempSec
			return wnd1sec
		except AttributeError:			
			print "%s missing from wnd1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
		
	def writeprt1(self, sec):
		try:
			TempSec = self.writepaneinfo(sec)
			section = sec.find("section")
			name = section.get("name")
			Scale = section.find("Scale")
			ScaleX = float(Scale.get("x"))
			ScaleY = float(Scale.get("y"))
			entry = section.findall("entry")
			TempSec += struct.pack(">I2f", len(entry), ScaleX, ScaleY)
			entrySec = ""
			TempSec2 = ""
			
			for i in entry:
				entryname = i.get("entryname")
				unk1 = int(i.find("unk1").text)
				unk2 = int(i.find("flag").text)
				entryoffset = 0
				extraoffset = 0
				tag = i.find("tag")
				extradata = i.find("extradata")
				if tag != None:
					entryoffset = 96 + (40 * len(entry)) + len(TempSec2) + WT.by4(len(name))
					tagtype = tag.get("type")
					if tagtype == "txt1":
						TempSec2 += self.writetxt1(tag)
					if tagtype == "pic1":
						TempSec2 += self.writepic1(tag)
					if tagtype == "wnd1":
						TempSec2 += self.writewnd1(tag)
					if tagtype == "bnd1":
						TempSec2 += self.writebnd1(tag)
					if tagtype == "prt1":
						TempSec2 += self.writeprt1(tag)
				if extradata != None:
					extraoffset = 96 + (40 * len(entry)) + len(TempSec2) + WT.by4(len(name))
					TempSec2 += binascii.unhexlify(extradata.text)
			
				entrySec += struct.pack(">24s2BH3I", entryname, unk1, unk2, 0, entryoffset, 0, extraoffset)
			
			entrySec += struct.pack(">%ds"%WT.by4(len(name)), name)
					
			TempSec += entrySec
			TempSec += TempSec2
			
			prt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
			prt1sec += TempSec
			return prt1sec
		except AttributeError:			
			print "%s missing from prt1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
		
	def writetxt1(self, sec):
		try:
			TempSec = self.writepaneinfo(sec)
			len1 = int(sec.find("restrictlength").text)
			len2 = int(sec.find("length").text)
			mat_num = self.MatErr(sec.find("material").text)
			font = sec.find("font")
			font_idx = self.fontfiles.index(font.get("Name"))
			temp = font.find("alignment")
			alignmentL = WT.RepresentsInt(temp.get("x"), types.originX)
			alignmentH = WT.RepresentsInt(temp.get("y"), types.originY) * 4
			alignment = alignmentL + alignmentH
			LineAlignment = WT.RepresentsInt(font.find("LineAlignment").text, types.TextAlign)
			ActiveShadows = int(font.find("ActiveShadows").text)
			unk1 = int(font.find("unk1").text)
			ItalicTilt = float(font.find("ItalicTilt").text)
			# StartOfTextOffset = int(font.find("OffsetStartOfText").text)		
			xsize = float(font.find("xsize").text)
			ysize = float(font.find("ysize").text)
			charsize = float(font.find("charsize").text)
			linesize = float(font.find("linesize").text)
			#callnameoffset = int(font.find("callnameoffset").text)
			
			colors = sec.find("topcolor")
			color1 = int(colors.get("R")) << 24
			color1 |= int(colors.get("G")) << 16
			color1 |= int(colors.get("B")) << 8
			color1 |= int(colors.get("A")) 
			colors = sec.find("bottomcolor")
			color2 = int(colors.get("R")) << 24
			color2 |= int(colors.get("G")) << 16
			color2 |= int(colors.get("B")) << 8
			color2 |= int(colors.get("A")) 
			
			Shadows = sec.find("Shadows")
			OffsetX = float(Shadows.find("OffsetX").text)
			OffsetY = float(Shadows.find("OffsetY").text)
			ScaleX = float(Shadows.find("ScaleX").text)
			ScaleY = float(Shadows.find("ScaleY").text)
			colors = Shadows.find("ShadowTopColor")
			ShadowTopColor = int(colors.get("R")) << 24
			ShadowTopColor |= int(colors.get("G")) << 16
			ShadowTopColor |= int(colors.get("B")) << 8
			ShadowTopColor |= int(colors.get("A")) 
			colors = Shadows.find("ShadowBottomColor")
			ShadowBottomColor = int(colors.get("R")) << 24
			ShadowBottomColor |= int(colors.get("G")) << 16
			ShadowBottomColor |= int(colors.get("B")) << 8
			ShadowBottomColor |= int(colors.get("A"))
			ShadowItalic = float(Shadows.find("ItalicTilt").text)
			unk3 = int(Shadows.find("unk3").text)
			
			Texttemp =sec.find("text").text
			if Texttemp == None:
				text = ""
			else:
				text = binascii.unhexlify(sec.find("text").text)
				
			while len(text) % 4 != 0:
				text += "\x00"
			callname = sec.find("callname").text
					
			TempSec += struct.pack(">4H4Bf3I4fI4f2IfI",len1, len2, mat_num, font_idx, alignment, LineAlignment, ActiveShadows, unk1, ItalicTilt , 164, color1, color2,
									xsize, ysize, charsize, linesize, 0, OffsetX, OffsetY, ScaleX, ScaleY, ShadowTopColor, ShadowBottomColor, ShadowItalic, unk3)
									
			TempSec += text
			if callname == None:
				pass				
			else:
				TempSec += struct.pack(">%ds"%WT.by4(len(callname)), callname)
			
			txt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
			txt1sec += TempSec
			
			return txt1sec
		except AttributeError:			
			print "%s missing from txt1 section" %WT.errinfo(traceback.format_exc())
			sys.exit(1)
		
	def writegrp1(self, sec):	
		TempSec2 = ""
		GroupName = sec.get("name")
		temp = sec.find('subs')
		if temp is not None:
			num_subs = len(temp.findall('sub'))
			subnames = temp.findall('sub')
			for i in subnames:
				TempSec2 += struct.pack('>24s', i.text)				
		else:		
			num_subs = 0
			
		if self.bflytVersion < 1282:
			TempSec = struct.pack(">24s2h",GroupName, num_subs,0)
		else:
			TempSec = struct.pack(">34sh",GroupName, num_subs)
			
		TempSec += TempSec2
		grp1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		grp1sec += TempSec
		return grp1sec
	
	def writecnt1(self, sec):
		PartType = sec.find("PartType")
		Partname = PartType.get("name")
		NameLength = WT.by4(len(Partname))
		parts = PartType.findall("parts")
		animParts = 0
		
		AnimPart = sec.find("AnimPart")
		
		if sec.find("dump") == None:
			firstSec = ""
			secondSec = ""
			thirdSec = ""
			AnimsOffset = []
			for i in parts:
				firstSec += struct.pack(">24s", i.text )
				
			
			if AnimPart != None:
				animParts = 1
				animfile = AnimPart.get("name")
				Anims = AnimPart.findall("Anims")
				AnimsOffset += [4*len(Anims)]			
				secondSec += struct.pack(">I%ds" %WT.by4(len(animfile)), len(Anims) + 1, animfile )
				
				names = struct.pack(">%ds"%WT.plusnull(len(Anims[0].text)),Anims[0].text)
				i = 1
				while i < len(Anims):
					
					AnimsOffset.append(len(names) + AnimsOffset[0])
					temp = struct.pack(">%ds"%WT.plusnull(len(Anims[i].text)),Anims[i].text)
					names += temp
					i += 1
					
				while len(names) % 4 != 0:
					names += "\x00"
					
				for k in AnimsOffset:
					thirdSec += struct.pack(">I", k)
				
				thirdSec += names
			
			else:
				Anims = 0
				
			thirdOffset = len(firstSec) + 28 + (NameLength * 2) + len(secondSec)
			TempSec = struct.pack(">2I2H2I%ds%ds" %(NameLength, NameLength), 28 + NameLength, 28 + (NameLength * 2), len(parts), animParts, thirdOffset, thirdOffset + len(thirdSec),Partname,Partname )
			TempSec += firstSec
			TempSec += secondSec
			TempSec += thirdSec
			TempSec += secondSec
			
		else:
			TempSec = binascii.unhexlify(sec.find("dump").text)
		
		cnt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		cnt1sec += TempSec
		
		
		return cnt1sec
		
	def writepaneinfo(self, sec):#84
		
		name = sec.get("name")
		temp = sec.find("visible")
		flag = int(temp.text) 
		temp = sec.find("TransmitAlpha2Children")
		flag |= int(temp.text) << 1
		temp = sec.find("PositionAdjustment")
		flag |= int(temp.text) << 2
		temp = sec.find("origin")
		originL = WT.RepresentsInt(temp.get("x"), types.originX)
		originH = WT.RepresentsInt(temp.get("y"), types.originY) * 4
		temp = sec.find("OriginOfParent")
		originPL = WT.RepresentsInt(temp.get("x"), types.originX)
		originPH = WT.RepresentsInt(temp.get("y"), types.originY) * 4
		parentorigin = (originPL + originPH) * 16
		origin = originL + originH + parentorigin
		temp = sec.find("alpha")
		alpha = int(temp.text)
		temp = sec.find("PartScaling")
		partscale = int(temp.text)
		temp = sec.find("translate")
		temp2 = temp.find("x")
		XTrans = float(temp2.text)
		temp2 = temp.find("y")
		YTrans = float(temp2.text)
		temp2 = temp.find("z")
		ZTrans = float(temp2.text)
		temp = sec.find("rotate")
		temp2 = temp.find("x")
		XRotate = float(temp2.text)
		temp2 = temp.find("y")
		YRotate = float(temp2.text)
		temp2 = temp.find("z")
		ZRotate = float(temp2.text)
		temp = sec.find("scale")
		temp2 = temp.find("x")
		XScale = float(temp2.text)
		temp2 = temp.find("y")
		YScale = float(temp2.text)
		temp = sec.find("size")
		temp2 = temp.find("x")
		width = float(temp2.text)
		temp2 = temp.find("y")
		height = float(temp2.text)
						
		TempSec = struct.pack(">4B32s10f",flag, origin, alpha, partscale, name, XTrans, YTrans, ZTrans, XRotate, YRotate, ZRotate, XScale, YScale, width, height)
		
		return TempSec
		
		
	def writeusd1(self, sec):
		TempSec = binascii.unhexlify(sec.find("dump").text)
		usd1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		usd1sec += TempSec
		return usd1sec
		
	def MatErr(self, data):
		try:
			mat = WT.RepresentsInt(data, self.MatList)
			return mat
		except ValueError:
			print "No data in mat1 for %s" %(data)
			sys.exit(1)
		
		
	def debugfile(self, data):
		try:
			with open("data.bin", "wb") as dirpath:
				dirpath.write(data)
		except:
			print "Destination file is in use"
			
			