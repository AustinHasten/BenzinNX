import struct, sys
from WriteTypes import Writer 
import binascii
WT = Writer()


class WriteBflan(object):

	def start(self, data, name):
		self.FileSections = 0
		self.OutFile = ""
		self.version = data.find("version")
		
		tags = self.version.findall("tag")		
		for i in tags:
			if i.get('type') == "pat1":
				self.OutFile += self.writepat1(i)
			if i.get('type') == "pai1":
				self.OutFile += self.writepai1(i)
		
		self.OutFile = self.header() + self.OutFile
		self.debugfile(self.OutFile)
		
		
	def header(self):
						
		return struct.pack(">4s4HI2H","FLAN",65279,20,int(self.version.get("Number")),0,int(len(self.OutFile)) + 20,self.FileSections,0)
			
	def writepat1(self, sec):
		data = list(sec)
		AnimOrder = int(data[0].text)
		Start = int(data[1].text)
		End = int(data[2].text)
		ChildBinding = int(data[3].text)
		First = data[4].text
		FirstOffset = 28
		SecondsOffset = WT.by4(len(First)) + FirstOffset
		data2 = list(data[5])
		FandS = struct.pack("%ds"%WT.by4(len(First)), First)
		for entry in data2:
			FandS += struct.pack(">28s",entry.text)
		
		TempSec = struct.pack(">2H2I2H2BH", AnimOrder, len(data2), FirstOffset, SecondsOffset, Start, End, ChildBinding, 0, 0)
		TempSec += FandS
		pat1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		pat1sec += TempSec
		self.FileSections += 1		
		return pat1sec
		
	def writepai1(self, sec):
		framesize = sec.get("framesize")
		flags = sec.get("flags")
		timgs = sec.findall("timg")
		entries = sec.findall("pane")
		timgSec = ""
		
		# Write timg section if there is one
		if len(timgs) != 0:
			timgOffset = [4*len(timgs)]
			timgNames = struct.pack(">%ds"%WT.plusnull(len(timgs[0].get("name"))),timgs[0].get("name"))
	
			i = 1
			while i < len(timgs):
				timgOffset.append(len(timgNames) + timgOffset[0])
				timgNames += struct.pack(">%ds"%WT.plusnull(len(timgs[i].get("name"))),timgs[i].get("name"))
				i += 1
				
			while len(timgNames) % 4 != 0:
				timgNames += "\x00"
				
			timgSec = struct.pack('>%sI' % len(timgOffset), *timgOffset)
			timgSec += timgNames
			
		TempSec = struct.pack(">H2B2HI", int(framesize), int(flags), 0, len(timgs), len(entries), len(timgSec) + 20)
		TempSec += timgSec
		
		baselength = len(TempSec) + 8
		entriesOffsets = [4*len(entries) + baselength]
		paneSec = self.PaneSection(entries[0])
		i = 1
		while i < len(entries):
			entriesOffsets.append(len(paneSec) + entriesOffsets[0])
			paneSec += self.PaneSection(entries[i])
			i += 1
		
		TempSec2 = struct.pack('>%sI' % len(entriesOffsets), *entriesOffsets)
		TempSec2 += paneSec
		TempSec += TempSec2		
		pai1sec = struct.pack(">4sI",sec.get('type'),int(len(TempSec))+8)
		pai1sec += TempSec
		self.FileSections += 1
		return pai1sec
	
	
	def PaneSection(self, pane):
		name = pane.get("name")
		tags = pane.findall("tag")
		is_material = pane.get("type")
		paneSec = struct.pack('>28s2BH' , name, len(tags), int(is_material), 0)
		
		TagOffsets = [4*len(tags) + len(paneSec)]
		taginfo = self.TagSection(tags[0])
	
		i = 1
		while i < len(tags):
			TagOffsets.append(len(taginfo) + TagOffsets[0])
			taginfo += self.TagSection(tags[i])
			i += 1
		
		TempSec = struct.pack('>%sI' % len(TagOffsets), *TagOffsets)
		TempSec += taginfo
		paneSec += TempSec
		return paneSec
	
	def TagSection(self, tag):
		tagtype = tag.get("type")
		entry_count = tag.findall("entry")
		taginfo = struct.pack('>4s4B' , tagtype, len(entry_count), 0, 0, 0)
		
		infoOffset = [4*len(entry_count) + len(taginfo)]
		entrySection = self.entrySection(entry_count[0], tagtype)
				
		i = 1
		while i < len(entry_count):
			infoOffset.append(len(entrySection) + infoOffset[0])
			entrySection += self.entrySection(entry_count[i], tagtype)
			i += 1
		
		TempSec = struct.pack('>%sI' % len(infoOffset), *infoOffset)
		TempSec += entrySection
		taginfo += TempSec
		return taginfo
		
	
	def entrySection(self, entry, tagtype):
		type1 = entry.get("type1")
		type2 = entry.get("type2")
		if len(entry.findall("triplet")) != 0:
			data_type = 512
			coord_count = entry.findall("triplet")
			TempSec = self.triplet(coord_count)
		elif len(entry.findall("pair")) != 0:
			data_type = 256			
			coord_count = entry.findall("pair")
			TempSec = self.pair(coord_count)
		
		entrySection = struct.pack('>2B3HI' , int(type1), int(type2), data_type, len(coord_count), 0, 12)
		entrySection += TempSec
		return entrySection
	
	def triplet(self, count):
		TempSec = ""
		for i in count:
			p1 = float(i[0].text)
			p2 = float(i[1].text)
			p3 = float(i[2].text)
			TempSec += struct.pack('>3f' , p1, p2, p3)
		
		return TempSec
		
	def pair(self, count):
		TempSec = ""
		for i in count:
			p1 = float(i[0].text)
			p2 = int(i[1].text)
			p3 = int(i[2].text)
			TempSec += struct.pack('>f2H' , p1, p2, p3)
		
		return TempSec
	
	
	def debugfile(self, data):
		
		with open("data.bin", "wb") as dirpath:
			dirpath.write(data)
			
			
			