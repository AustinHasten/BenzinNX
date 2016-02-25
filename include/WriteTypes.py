
import struct, sys

class Writer(object):
	
	def by4(self,length):
		temp = length + 1		
		while  temp % 4 != 0:
			temp += 1
		return temp

	def plusnull(self,length):
		return length + 1

	def errinfo(self, err):
		exceptiondata = err.splitlines()
		exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
		return exceptionarray[-1].split('"')[1]
		
	def RepresentsInt(self, data, list):
		try: 
			number = int(data)
			return number
		except ValueError:
			try:
				return list.index(data)
			except:
				print "%s is a unknown entry"%data
				sys.exit(1)
			