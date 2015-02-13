import struct
from WriteTypes import Writer 
WT = Writer()


class WriteBflyt(object):

	def start(self, data, name):
	
		self.FileSections = 0
		self.OutFile = ""
		self.version = data.find("version")
		
		tags = self.version.findall("tag")		
		for i in tags:
			print i.get('type')
			if i.get('type') == "lyt1":
				self.OutFile += self.writelyt1(i)
			elif i.get('type') == "txl1":
				self.OutFile += self.writetxl1(i)
			elif i.get('type') == "fnl1":
				self.OutFile += self.writetxl1(i)
		
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
		
		
		
	def debugfile(self, data):
		
		with open("data.bin", "w") as dirpath:
			dirpath.write(data)
			
			
			