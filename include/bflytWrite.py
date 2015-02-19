import struct, sys
from WriteTypes import Writer 
import binascii
WT = Writer()


class WriteBflyt(object):

	def start(self, data, name):
	
		self.FileSections = 0
		self.OutFile = ""
		self.version = data.find("version")
		
		tags = self.version.findall("tag")		
		for i in tags:
			#print i.get('type')
			if i.get('type') == "lyt1":
				self.OutFile += self.writelyt1(i)
			elif i.get('type') == "txl1":
				self.OutFile += self.writetxl1(i)
			elif i.get('type') == "fnl1":
				self.OutFile += self.writetxl1(i)
			elif i.get('type') == "mat1":
				self.OutFile += self.writemat1(i)
			elif i.get('type') == "pan1":
				self.OutFile += self.writepan1(i)
			elif i.get('type') == "pas1":
				self.OutFile += self.writepas1(i)
			elif i.get('type') == "pic1":
				self.OutFile += self.writepic1(i)
			elif i.get('type') == "bnd1":
				self.OutFile += self.writepan1(i)
			elif i.get('type') == "wnd1":
				self.OutFile += self.writewnd1(i)
			elif i.get('type') == "txt1":
				self.OutFile += self.writetxt1(i)
			elif i.get('type') == "prt1":
				self.OutFile += self.writeprt1(i)
			elif i.get('type') == "pae1":
				self.OutFile += self.writepas1(i)
			elif i.get('type') == "grp1":
				self.OutFile += self.writegrp1(i)
			elif i.get('type') == "grs1":
				self.OutFile += self.writepas1(i)
			elif i.get('type') == "gre1":
				self.OutFile += self.writepas1(i)
			elif i.get('type') == "cnt1":
				self.OutFile += self.writecnt1(i)
		
		self.OutFile = self.header() + self.OutFile
		self.debugfile(self.OutFile)
		
		
	def header(self):
						
		return struct.pack(">4s4HI2H","FLYT",65279,20,int(self.version.get("Number")),0,int(len(self.OutFile)) + 20,self.FileSections,0)
			
	def writelyt1(self, sec):
		data = list(sec)
		drawnFromMiddle = int(data[0].text)		
		pad = 0
		width = float(data[1].text)
		height = float(data[2].text)
		unk1 = float(data[3].text)
		unk2 = float(data[4].text)
		filename = data[5].text
		TempSec = struct.pack(">4b4f%ds"%WT.by4(len(filename)),drawnFromMiddle,pad,pad,pad,width,height,unk1,unk2,filename)
		lyt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		lyt1sec += TempSec
		self.FileSections += 1
		return lyt1sec
		
	def writetxl1(self, sec):
		temp = sec.find("entries")
		data = list(temp)
		NumTextures = len(data)
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
		txl1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec))+12,NumTextures,0)
		txl1sec += TempSec
		self.FileSections += 1
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
		self.FileSections += 1
		return fnl1sec
		
	def writemat1(self, sec):
		temp = sec.findall("entries")
		data = list(temp)
		self.MatList = []
		MatOffset = [4*len(data)+12]
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
			if int(flags) != 0:
				TempSec += binascii.unhexlify(i.find("dump").text)
				
			if len(MatOffset) < len(data):
				MatOffset.append(MatOffset[-1] + len(TempSec))
				
			fullTempSec += TempSec
			
		TempSec2 = struct.pack('>%sI' % len(MatOffset), *MatOffset)
		TempSec2 += fullTempSec
		mat1sec = struct.pack(">4sI2h",sec.get('type'),int(len(TempSec2))+12,len(data),0)
		mat1sec += TempSec2
		self.FileSections += 1
		return mat1sec
				
	def writepan1(self, sec):
		TempSec = self.writepaneinfo(sec)
		pan1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		pan1sec += TempSec
		self.FileSections += 1		
		return pan1sec
				
	def writepas1(self, sec):
		pas1sec = struct.pack(">4sI",sec.get('type'),8)
		self.FileSections += 1	
		return pas1sec
		
	def writepic1(self, sec):
		TempSec = self.writepaneinfo(sec)
		i = 0
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
		material = sec.find("material").text
		while i < len(self.MatList):
			if material != self.MatList[i]:
				pass
			else:
				mat_num = i
				break
			i += 1
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
		self.FileSections += 1				
		return pic1sec
	
	def writewnd1(self, sec):
		TempSec = self.writepaneinfo(sec)
		TempSec += binascii.unhexlify(sec.find("dump").text)
		
		wnd1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		wnd1sec += TempSec
		self.FileSections += 1
		return wnd1sec
		
	def writeprt1(self, sec):
		TempSec = self.writepaneinfo(sec)
		TempSec += binascii.unhexlify(sec.find("dump").text)
		
		prt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		prt1sec += TempSec
		self.FileSections += 1
		return prt1sec
		
		
	def writetxt1(self, sec):
		TempSec = self.writepaneinfo(sec)
		TempSec += binascii.unhexlify(sec.find("dump").text)
		
		txt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		txt1sec += TempSec
		self.FileSections += 1
		return txt1sec
		
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
		self.FileSections += 1
		return grp1sec
	
	def writecnt1(self, sec):
		TempSec = binascii.unhexlify(sec.find("dump").text)
		
		cnt1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		cnt1sec += TempSec
		self.FileSections += 1
		return cnt1sec
		
	def writepaneinfo(self, sec):
		
		name = sec.get("name")
		temp = sec.find("visible")
		flag = int(temp.text) 
		temp = sec.find("WidescreenAffected")
		flag |= int(temp.text) << 1
		temp = sec.find("flag")
		flag |= int(temp.text) << 2
		temp = sec.find("origin")
		originL = int(temp.get("x"))
		originH = int(temp.get("y")) * 3
		origin = originL + originH
		temp = sec.find("alpha")
		alpha = int(temp.text)
		temp = sec.find("unk")
		unk = int(temp.text)
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
		
	def debugfile(self, data):
		
		with open("data.bin", "wb") as dirpath:
			dirpath.write(data)
			
			
			