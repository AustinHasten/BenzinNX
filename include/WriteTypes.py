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
                print(f"{data} is a unknown entry")
                sys.exit(1)
            
    def BitInsert(self, value, newValue, count, start):
        mask = 0
        i = start
        while i < start+count:
            mask |= (0x80000000 >> i)
            i +=1
            
        value &= not(mask)
        value |= (newValue << (32 - (start + count))) & mask
        return value
