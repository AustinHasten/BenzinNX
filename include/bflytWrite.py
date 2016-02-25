import struct, sys, traceback
from WriteTypes import Writer 
import binascii
WT = Writer()
import types


class WriteBflyt(object):

	def start(self, data, name, output):
		self.FileSections = 0
		self.texturefiles = []
		self.OutFile = ""
		self.version = data.find("version")
		
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
				self.OutFile += self.writetxl1(i)
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
		except:
			print "Destination file is in use"
		
		
	def header(self):
						
		return struct.pack(">4s4HI2H","FLYT",65279,20,int(self.version.get("Number")),0,int(len(self.OutFile)) + 20,self.FileSections,0)
			
	def writelyt1(self, sec):
		try:
			drawnFromMiddle = int(sec.find("drawnFromMiddle").text)		
			pad = 0
			width = float(sec.find("width").text)
			height = float(sec.find("height").text)
			unk1 = float(sec.find("unk1").text)
			unk2 = float(sec.find("unk2").text)
			filename = sec.find("filename").text
			TempSec = struct.pack(">4b4f%ds"%WT.by4(len(filename)),drawnFromMiddle,pad,pad,pad,width,height,unk1,unk2,filename)
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
		
		i = 1
		while i < len(data):
			FilenameOffset.append(len(names) + FilenameOffset[0])
			temp = struct.pack(">%ds"%WT.plusnull(len(data[i].text)),data[i].text)
			names += temp
			i += 1
			
		while len(names) % 4 != 0:
			names += "\x00"
		
		TempSec = struct.pack('>%sI' % len(FilenameOffset), *FilenameOffset)
		
		TempSec += names
		fnl1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec))+12,NumTextures,0)
		fnl1sec += TempSec
		return fnl1sec
		
	def writemat1(self, sec):
		try:
			temp = sec.findall("entries")
			self.MatList = []
			MatOffset = [4*len(temp)+12]
			fullTempSec = ""
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
				flags = i.find("flags").text
				TempSec = struct.pack(">28s8BI",name,int(forecolR),int(forecolG),int(forecolB),int(forecolA),
										int(backcolR),int(backcolG),int(backcolB),int(backcolA),int(flags))
										
				texref = i.findall("texture")
				if i.find("texture") != None:
					for loop in texref:
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
						XTrans = float(loop.find("XTrans").text)
						YTrans = float(loop.find("YTrans").text)
						Rotate = float(loop.find("Rotate").text)
						XScale = float(loop.find("XScale").text)
						YScale = float(loop.find("YScale").text)
						TempSec += struct.pack(">5f", XTrans, YTrans, Rotate, XScale, YScale)
										
				if int(flags) != 0:
					TempSec += binascii.unhexlify(i.find("dump").text)
					
				if len(MatOffset) < len(temp):
					MatOffset.append(MatOffset[-1] + len(TempSec))
					
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
			coordinate = wnd.findall("coordinate")		
			FrameCount = int(wnd.find("FrameCount").text)
			unk1 = int(wnd.find("unk1").text)
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
			part1 = struct.pack('>4f4B2I16BH2B', float(coordinate[0].text), float(coordinate[1].text), float(coordinate[2].text), float(coordinate[3].text),
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
			unkfloat = section.find("unkfloat")
			unkfloat1 = float(unkfloat.get("x"))
			unkfloat2 = float(unkfloat.get("y"))
			entry = section.findall("entry")
			TempSec += struct.pack(">I2f", len(entry), unkfloat1, unkfloat2)
			entrySec = ""
			TempSec2 = ""
			
			for i in entry:
				entryname = i.get("entryname")
				unk1 = int(i.find("unk1").text)
				unk2 = int(i.find("unk2").text)
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
			mat_num = self.MatErr(sec.find("material").get("name"))
			font = sec.find("font")
			font_idx = int(font.get("index"))
			temp = font.find("alignment")
			alignmentL = int(temp.get("x"))
			alignmentH = int(temp.get("y")) * 3
			alignment = alignmentL + alignmentH
			LineAlignment = int(font.find("LineAlignment").text)
			unk = int(font.find("unk").text)
			name_offs = int(font.find("name_offs").text)
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
			
			newstuff = sec.find("newstuff")
			unkfloat = float(newstuff.find("unkfloat").text)
			unkfloat1 = float(newstuff.find("unkfloat1").text)
			unkfloat2 = float(newstuff.find("unkfloat2").text)
			unkfloat3 = float(newstuff.find("unkfloat3").text)
			colors = newstuff.find("unkcolor1")
			unkcolor1 = int(colors.get("R")) << 24
			unkcolor1 |= int(colors.get("G")) << 16
			unkcolor1 |= int(colors.get("B")) << 8
			unkcolor1 |= int(colors.get("A")) 
			colors = newstuff.find("unkcolor2")
			unkcolor2 = int(colors.get("R")) << 24
			unkcolor2 |= int(colors.get("G")) << 16
			unkcolor2 |= int(colors.get("B")) << 8
			unkcolor2 |= int(colors.get("A")) 		
			unk2 = int(newstuff.find("unk2").text)
			
			text = binascii.unhexlify(sec.find("text").text)		
			while len(text) % 4 != 0:
				text += "\x00"
			callname = sec.find("callname").text
					
			TempSec += struct.pack(">4H2BH4I4f2I3f3I",len1, len2, mat_num, font_idx, alignment, LineAlignment, unk, name_offs , 160, color1, color2,
									xsize, ysize, charsize, linesize, 160 + len(text), unkfloat, unkfloat1, unkfloat2, unkfloat3, unkcolor1, unkcolor2, unk2)
									
			TempSec += text
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
		TempSec = struct.pack(">24s2H",GroupName, num_subs, 0)
		TempSec += TempSec2
		grp1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		grp1sec += TempSec
		return grp1sec
	
	def writecnt1(self, sec):
		name = sec.get("name")
		NameLength = WT.by4(len(name))
		if sec.find("dump") == None:
			first = sec.findall("first")
			second = sec.findall("second")
			firstSec = ""
			secondSec = ""
			for i in first:
				firstSec += struct.pack(">24s",i.text)
			
			Offset = []
			try:
				secondSec = struct.pack(">%ds"%WT.plusnull(len(second[0].text)),second[0].text)
				Offset.append(4*len(second))
			except:
				pass
			i = 1
			while i < len(second):
				Offset.append(len(secondSec) + Offset[0])
				if second[i].text != None:
					temp = struct.pack(">%ds"%WT.plusnull(len(second[i].text)),second[i].text)
				else:
					temp = struct.pack(">1s","")
				secondSec += temp
				i += 1
				
			while len(secondSec) % 4 != 0:
				secondSec += "\x00"
				
			TempSec2 = struct.pack('>%sI' % len(Offset), *Offset)
			TempSec2 += secondSec
			TempSec = struct.pack(">I2H%ds" %NameLength, NameLength + 16, len(first), len(second), name)
			TempSec += firstSec
			TempSec += TempSec2
			
		else:
			TempSec = binascii.unhexlify(sec.find("dump").text)
		
		cnt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		cnt1sec += TempSec
		return cnt1sec
		
	def writepaneinfo(self, sec):
		
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
						
		TempSec = struct.pack(">4B32s10f",flag, origin, alpha, unk, name, XTrans, YTrans, ZTrans, XRotate, YRotate, ZRotate, XScale, YScale, width, height)
		
		return TempSec
		
	def MatErr(self, data):
		try:
			mat = self.MatList.index(data)
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
			
			