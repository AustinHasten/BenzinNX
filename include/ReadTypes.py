
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
			
	def BitExtract(self, value, count, start):
		# this function relies on heavy compiler optimisation to be efficient :p
		mask = 0
		i = start
		while i < start+count:
			mask |= (0x80000000 >> i)
			i +=1
		
		return (value & mask) >> (32 - (start + count))	
			
	def bit_extract(self, num, start, end):
	
		if (end == 100):
			end = start
		mask = 0
		first = 0
		firstMask = 1
		while first < 31-start+1:
			firstMask *= 2
			first += 1
			
		firstMask -= 1
		secondMask = 1
		
		first=0
		while first < 31-end:
			secondMask *=2
			first += 1
			
		secondMask -= 1;
		mask = firstMask - secondMask
		ret = (num & mask) >> (31 - end)
		return ret