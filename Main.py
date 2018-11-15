# BenzinU by Diddy81
# Modified by Austin Hasten

import os, sys
from include import *
from lxml import etree
from urllib.request import urlopen

def main():
    print(sys.argv[1])
    UseMatNames, output = options()
    name, ext = os.path.splitext(sys.argv[1])
  
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
    header = data[0:4].decode('utf-8')
    if header == "FLYT":
        bflytread = bflytRead.ReadBflyt(data, output)
    elif header == "FLAN":
        bflanread = bflanRead.ReadBflan(data, output)
    else:
        try:
            tree = etree.parse(sys.argv[1])
            data = tree.getroot()
            if data.tag == "xmflyt":
                bflytwrite = bflytWrite.WriteBflyt()
                bflytwrite.start(data, name, output)
            elif data.tag == "xmflan":
                bflanwrite = bflanWrite.WriteBflan()
                bflanwrite.start(data, name, output)
            else:
                print("Unknown File Format!")
                sys.exit(1)
        except:
            e = sys.exc_info()[0]
            print( "<p>Error: %s</p>" % e )
            print("Something went wrong!")
            sys.exit(1)
            
            
def options():
    usage = """if converting bflyt/bflan to xmflyt/xmflan:
Usage: BenzinU input [option] [output]
    options:
        -m          use Material numbers instead of names
    output:
        output file name is optional 
        
if converting xmflyt/xmflan to bflyt/bflan:
Usage: BenzinU input [output]
    output:
        output file name is optional """
    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)
    if len(sys.argv) >= 3:  
        if sys.argv[2].lower() == "-m":
            UseMatNames = False
            try:
                output = sys.argv[3]
            except:
                output = None               
        elif sys.argv[2].startswith("-"):
            print("Unknown option given")
            print(usage)
            sys.exit(1)
        else:
            UseMatNames = True
            output = sys.argv[2]
    elif len(sys.argv) == 2:
        try:
            output = sys.argv[2]
        except:
            output = None
        UseMatNames = True      
    else:
        print(usage)
        sys.exit(1)
        
    return UseMatNames, output
        
if __name__ == "__main__":
    main()
