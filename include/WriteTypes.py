
import struct

class Writer(object):
	
	def by4(self,length):
		temp = length + 1		
		while  temp % 4 != 0:
			temp += 1
		return temp

	def plusnull(self,length):
		return length + 1
