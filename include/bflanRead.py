import re
import sys
from . import types
from lxml import etree, objectify
from struct import unpack_from, calcsize

class ReadBflan(object):
    def __init__(self, data, output):
        self.root = objectify.Element('xmflan')
        self.position = 0
        self.data = data
        self.read_header()
        etree.ElementTree(self.root).write(output, pretty_print=True)
        print("File converted.")

    def unpackk(self, formstr, increment=True):
        rval = unpack_from(formstr, self.data, self.position)
        self.position += calcsize(formstr) if increment else 0
        return rval if len(rval) > 1 else rval[0]

    def unpackkstr(self, strlen, increment=True):
        return self.unpackk(str(strlen) + 's', increment).decode('utf-8')

    def unpackkvarstr(self):
        strlen = self.data[self.position:].find(b'\x00')
        string = self.unpackkstr(strlen)
        paddinglen = re.search(b'[^\x00]', self.data[self.position:]).start()
        self.position += paddinglen
        return string

    def read_header(self):
        magic = self.unpackkstr(4)
        routing = {'FLAN':self.read_bflanheader, 'pat1':self.read_pat, 'pai1':self.read_pai}
        try:
            routing[magic]()
        except KeyError:
            print(f"No code for {magic} section at {self.position}.")
        
    def read_bflanheader(self):
        bflanheader = types.bflanheader_tup(*self.unpackk('HHHHIHH'))
        self.newroot = objectify.SubElement(self.root, 'version', Number=str(bflanheader.version))
        self.read_header()
        
    def read_pat(self):
        pat_start_pos = self.position - 4
        pat = types.pat_tup(*self.unpackk('IHHIIHHBBH'))

        self.position = pat_start_pos + pat.firstoffset
        first = self.unpackkvarstr()
        
        tag = objectify.SubElement(self.newroot, 'tag', type='pat1')
        tag.AnimOrder = pat.animorder
        tag.StartOfFile = pat.start
        tag.EndOfFile = pat.end
        tag.ChildBinding = pat.childbinding
        tag.First = first

        strngs2 = objectify.SubElement(tag, 'AnimatedGroups')
        self.position = pat_start_pos + pat.secondsoffset
        strngs2.Groupname = [ self.unpackkvarstr() for _ in range(pat.numseconds) ]

        self.read_header()
        
    def read_pai(self):
        pai_start_pos = self.position - 4
        pai = types.pai_tup(*self.unpackk('IHBBHHI'))

        tag = objectify.SubElement(self.newroot, 'tag', type='pai1')
        tag.attrib['framesize'] = str(pai.framesize)
        tag.attrib['flags'] = str(pai.flags)

        timgs_offsets = [ self.unpackk('I') for _ in range(pai.numtimgs) ]
        for timgs_offset in timgs_offsets:
            self.position = pai_start_pos + 20 + timgs_offset
            timgs = objectify.SubElement(tag, 'timg', name=self.unpackkvarstr())

        self.position = pai_start_pos + pai.entryoffset
        pane_offsets = [ self.unpackk('I') for _ in range(pai.numentries) ]
        for pane_offset in pane_offsets:
            self.read_pane(pai_start_pos, pane_offset)

    def read_pane(self, pai_start_pos, pane_offset):
        self.position = pai_start_pos + pane_offset
        name = self.unpackkvarstr()
        entry = types.entry_tup(*self.unpackk('BBH'))
        pane = objectify.SubElement(tag, 'pane', name=name, type=str(entry.is_material))

        tag_offsets = [ self.unpackk('I') for _ in range(entry.num_tags) ]
        for tag_offset in tag_offsets:
            self.read_tag(pai_start_pos, pane_offset, tag_offset)

    def read_tag(self, pai_start_pos, pane_offset, tag_offset):
        self.position = pai_start_pos + pane_offset + tag_offset
        typetree = objectify.SubElement(pane, 'tag')
        tag_start_pos = self.position
        tag_type = self.unpackkstr(4)
        # TODO Handle this more elegantly if possible.
        if tag_type == ',\x00\x00\x00':
            tag_type = self.unpackkstr(4)
        typetree.attrib['type'] = tag_type
        entry_count = self.unpackk('B')
        pad = self.unpackk('3B')
            
        tag_data_offsets = [ self.unpackk('I') for _ in range(entry_count) ]
        for tag_data_offset in tag_data_offsets:
            self.read_tag_data(tag_start_pos, tag_data_offset)

    def read_tag_data(self, tag_start_pos, tag_data_offset):
        self.position = tag_start_pos + tag_data_offset
        tag_data = types.tag_data_tup(*self.unpackk('BBHHHI'))
        try:
            typename = types.typedict[tag_type][tag_data.type2]
        except KeyError:
            typename = str(tag_data.type2)

        entry = objectify.SubElement(typetree, 'entry', type1=str(tag_data.type1), type2=typename)
        if tag_data.datatype == 2:
            self.triplet(tag_data.coordcount, entry)
        elif tag_data.datatype == 1:
            self.pair(tag_data.coordcount, entry)
    
    def triplet(self, count, entry):
        for _ in range(count):
            info = objectify.SubElement(entry, 'triplet')
            info.frame, info.value, info.blend = self.unpackk('3f')

    def pair(self, count, entry):
        for _ in range(count):
            info = objectify.SubElement(entry, 'pair')
            info.frame, info.data2, info.padding = self.unpackk('fHH')
