import sys, struct
from lxml import etree
from ReadTypes import Reader 
RT = Reader()
import types

class ReadBflan(object):

    def start(self, data, pos, name, output):
        self.root = etree.Element("xmflan")
        self.checkheader(data, pos)
        RT.indent(self.root)
        if output == None:
            with open(name + '.xmlan', "w") as dirpath:
                dirpath.write(etree.tostring(self.root))
        else:
            with open(output, "w") as dirpath:
                dirpath.write(etree.tostring(self.root))
    
    def checkheader(self, data, pos):
        magic = data[pos:pos + 4]
        if magic == "FLAN":
            self.bflanHeader(data, pos)
        elif magic == "pat1":
            self.pat1section(data, pos)
        elif magic == "pai1":
            self.pai1section(data, pos)
        elif len(data) == pos:
            print "File Converted"            
        else:
            print "No code for %s section at %s" %(magic, hex(pos))
            #sys.exit(1)
        
    def ReadMagic(self, data, pos):
        magic = data[pos:pos + 4]; pos += 4
        seclength = RT.uint32(data, pos);pos += 4
        return magic,seclength,pos
        
    def bflanHeader(self, data, pos):
        bflanmagic = data[0:4]; pos += 4
        endian = RT.uint16(data, pos);pos += 2
        if endian == 65534: #0xFFFE - Little Endian
            pass
        else:
            print("Big endian not supported!")
            sys.exit(1)
        FirstSectionOffsetree = RT.uint16(data, pos);pos += 2    # Should be 20
        version = RT.uint16(data, pos);pos += 2     # Always 0x0202
        pad1 = RT.uint16(data, pos);pos += 2         # Padding
        filesize = RT.uint32(data, pos);pos += 4    # Full Filesize
        sections = RT.uint16(data, pos);pos += 2    # Number of sections
        pad2 = RT.uint16(data, pos);pos += 2         # Padding
        self.newroot = etree.SubElement(self.root, "version", Number=str(version))
        self.checkheader(data, pos)    
        
    def pat1section(self, data, pos):
        StartPatPos = pos
        pat1magic, pat1length, pos = self.ReadMagic(data,pos)            # read magic & section length
        AnimOrder = RT.uint16(data, pos);pos += 2
        Num_Seconds = RT.uint16(data, pos);pos += 2
        FirstOffset = RT.uint32(data, pos);pos += 4
        SecondsOffset = RT.uint32(data, pos);pos += 4
        Start = RT.uint16(data, pos);pos += 2
        End = RT.uint16(data, pos);pos += 2
        ChildBinding = RT.uint8(data, pos);pos += 1
        pad = RT.uint8(data, pos);pos += 1
        pad1 = RT.uint16(data, pos);pos += 2
        pos = StartPatPos + FirstOffset
        First = RT.getstr(data[pos:])
        
        tag = etree.SubElement(self.newroot, "tag", type="pat1")
        etree.SubElement(tag, "AnimOrder").text = str(AnimOrder)
        etree.SubElement(tag, "StartOfFile").text = str(Start)
        etree.SubElement(tag, "EndOfFile").text = str(End)
        etree.SubElement(tag, "ChildBinding").text = str(ChildBinding)        
        etree.SubElement(tag, "First").text = str(First)
        strngs2 = etree.SubElement(tag, "AnimatedGroups")
        pos = StartPatPos + SecondsOffset
        i = 0
        while i < Num_Seconds:
            GroupName = RT.getstr(data[pos:]);pos += 28
            etree.SubElement(strngs2, "Groupname").text = str(GroupName)
            i += 1

        # Skip 8 bytes of padding introduced in NX files.
        pos += 8
            
        self.checkheader(data, pos)    
        
    def pai1section(self, data, pos):
        StartPaiPos = pos
        pai1magic, pai1length, pos = self.ReadMagic(data,pos)            # read magic & section length
        framesize = RT.uint16(data, pos);pos += 2
        flags = RT.uint8(data, pos);pos += 1
        pad = RT.uint8(data, pos);pos += 1
        num_timgs = RT.uint16(data, pos);pos += 2
        num_entries = RT.uint16(data, pos);pos += 2
        entry_offset = RT.uint32(data, pos);pos += 4
        
        tag = etree.SubElement(self.newroot, "tag", type="pai1")
        tag.attrib['framesize'] = str(framesize)
        tag.attrib['flags'] = str(flags)
        
        TimgsOffsets = []
        i = 0
        if num_timgs > 0:
            while i < num_timgs:
                TimgsOffsets.append(RT.uint32(data, pos));pos += 4
                i += 1
            for value in TimgsOffsets:
                pos = StartPaiPos + 20 + value
                Timgs = etree.SubElement(tag, "timg")
                Timgs.attrib['name'] = RT.getstr(data[pos:])
        
        pos = StartPaiPos + entry_offset
        OffsetList = []
        i = 0
        while i < num_entries:
            OffsetList.append(RT.uint32(data, pos));pos += 4
            i += 1
            
        for item in OffsetList:
            pos = StartPaiPos + item
            pane = etree.SubElement(tag, "pane")
            name = RT.getstr(data[pos:]);pos += 28
            num_tags = RT.uint8(data, pos);pos += 1
            is_material = RT.uint8(data, pos);pos += 1
            pad = RT.uint16(data, pos);pos += 2
            
            pane.attrib['name'] = name
            pane.attrib['type'] = str(is_material)
                        
            TagOffsets = []
            i = 0
            while i < num_tags:
                TagOffsets.append(RT.uint32(data, pos));pos += 4
                i += 1
                
            for offset in TagOffsets:
                pos = StartPaiPos + item + offset
                typetree = etree.SubElement(pane, "tag")
                TagStartPos = pos
                tagtype = data[pos:pos + 4];pos += 4
                typetree.attrib['type'] = tagtype
                
                entry_count = RT.uint8(data, pos);pos += 1
                pad = RT.uint24(data, pos);pos += 3
                Offsets = []
                i = 0
                while i < entry_count:
                    Offsets.append(RT.uint32(data, pos));pos += 4
                    i += 1
                    
                for offset1 in Offsets:
                    pos = TagStartPos + offset1
                    type1 = RT.uint8(data, pos);pos += 1
                    type2 = RT.uint8(data, pos);pos += 1
                    data_type = RT.uint16(data, pos);pos += 2
                    coord_count = RT.uint16(data, pos);pos += 2
                    pad1 = RT.uint16(data, pos);pos += 2
                    OffsetToTagData = RT.uint32(data, pos);pos += 4
                    
                    typename = self.GetTypeName(tagtype, type2)
                    
                    entry = etree.SubElement(typetree, "entry")
                    entry.attrib['type1'] = str(type1)
                    entry.attrib['type2'] = typename
                    
                    if data_type == 512:
                        self.triplet(data, pos, entry, coord_count)
                        
                    elif data_type == 256:
                        self.pair(data, pos, entry, coord_count)

        
    
    def GetTypeName(self, tagtype, type2):
        try:
            if tagtype == "FLPA":
                typename = types.FLPAtype2[type2]
            elif tagtype == "FLVI":
                typename = types.FLVItype2[type2]
            elif tagtype == "FLVC":
                typename = types.FLVCtype2[type2]
            elif tagtype == "FLMC":
                typename = types.FLMCtype2[type2]
            elif tagtype == "FLTS":
                typename = types.FLTStype2[type2]
            elif tagtype == "FLTP":
                typename = types.FLTPtype2[type2]
            elif tagtype == "FLIM":
                typename = types.FLIMtype2[type2]
                
            return typename
        except:
            return str(type2)
        
        
        
    def triplet(self, data, pos, tag, count):
        i = 0
        while i < count:
            p1 = RT.float4(data, pos);pos += 4
            p2 = RT.float4(data, pos);pos += 4
            p3 = RT.float4(data, pos);pos += 4
            info = etree.SubElement(tag, "triplet")
            etree.SubElement(info, "frame").text = str(p1)
            etree.SubElement(info, "value").text = str(p2)
            etree.SubElement(info, "blend").text = str(p3)            
            i += 1
            
    def pair(self, data, pos, tag, count):
        i = 0
        while i < count:
            p1 = RT.float4(data, pos);pos += 4
            p2 = RT.uint16(data, pos);pos += 2
            p3 = RT.uint16(data, pos);pos += 2
            info = etree.SubElement(tag, "pair")
            etree.SubElement(info, "frame").text = str(p1)
            etree.SubElement(info, "data2").text = str(p2)
            etree.SubElement(info, "padding").text = str(p3)            
            i += 1
        
        
    def debugfile(self, data):
        
        with open("data.bin", "w") as dirpath:
            dirpath.write(data)
            
            
