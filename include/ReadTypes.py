
import struct

class Reader(object):
	
	def by4(self,length):		
		while  length % 4 != 0:
			length += 1
		return length
		
	def uint8(self, data, pos):
		return struct.unpack(">B", data[pos:pos + 1])[0]
		
	def uint16(self, data, pos):
		return struct.unpack(">H", data[pos:pos + 2])[0]
		
	def uint24(self, data, pos):
		return struct.unpack(">I", "\00" + data[pos:pos + 3])[0]
		
	def uint32(self, data, pos):
		return struct.unpack(">I", data[pos:pos + 4])[0]
		
	def float4(self, data, pos):
		return struct.unpack(">f", data[pos:pos + 4])[0]
		
	def getstr(self,data):
		x = data.find("\x00")
		if x != -1:
			return data[:x]
		else:
			return data