
import struct

class Reader(object):
	
	def by4(self,length):		
		while  length % 4 != 0:
			length += 1
		return length
	
	def hexstr(self, data, length): #Convert input into hex string
		return hex(data).lstrip("0x").rstrip("L").zfill(length).upper()
	def binr(byte):
		return bin(byte).lstrip("0b").zfill(8)
	def uint8(self, data, pos):
		return struct.unpack(">B", data[pos:pos + 1])[0]
	def uint16(self, data, pos):
		return struct.unpack(">H", data[pos:pos + 2])[0]
	def uint24(self, data, pos):
		return struct.unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
	def uint32(self, data, pos):
		return struct.unpack(">I", data[pos:pos + 4])[0]
	def float4(self, data, pos):
		return struct.unpack(">f", data[pos:pos + 4])[0]
	def check(length, size, percent, count):
		length = float(length);size = float(size)
		test = round(length / size, 2) #Percent complete as decimal
		test = test * 100 #Percent
		if test % count == 0:
			if percent != test: #New Number
				print(str(test)[:-2] + "%")
				percent = test
		return percent
	def calchash(name, multiplier):
		result = 0
		for x in xrange(len(name)):
			result = ord(name[x]) + result * multiplier
		return result
	def getstr(self,data):
		x = data.find("\x00")
		if x != -1:
			return data[:x]
		else:
			return data
	def intify(out, data, length = 0):
		if type(data) == str:
			for x in xrange(len(data)):
				out.append(ord(data[x]))
		if type(data) == int:
			data = hexstr(data, length * 2)
			for x in xrange(length):
				out.append(int(data[x * 2:(x * 2) + 2], 16))
		return out
		
	
	def indent(self, elem, level=0):
		i = "\n"  + level*"	"
		if len(elem):
			if not elem.text or not elem.text.strip():
				elem.text = i + "	"
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
			for elem in elem:
				self.indent(elem, level+1)
			if not elem.tail or not elem.tail.strip():
				elem.tail = i
		else:
			if level and (not elem.tail or not elem.tail.strip()):
				elem.tail = i

