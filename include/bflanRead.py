import re
import sys
from . import types
from lxml import etree
from collections import namedtuple
from struct import unpack_from, calcsize

class ReadBflan(object):
    def __init__(self, data, output):
        self.root = etree.Element('xmflan')
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
        routing = {'FLAN':self.read_bflanheader, 'pat1':self.read_pat1section, 'pai1':self.read_pai1section}
        try:
            routing[magic]()
        except KeyError:
            print(f"No code for {magic} section at {self.position}.")
        
    def read_bflanheader(self):
        bflanheader = types.bflanheader_tup(*self.unpackk('HHHHIHH'))
        self.newroot = etree.SubElement(self.root, 'version', Number=str(bflanheader.version))
        self.read_header()
        
    def read_pat1section(self):
        pat_start_pos = self.position - 4
        pat1section = types.pat1section_tup(*self.unpackk('IHHIIHHBBH'))

        self.position = pat_start_pos + pat1section.firstoffset
        first = self.unpackkvarstr()
        
        tag = etree.SubElement(self.newroot, 'tag', type='pat1')
        etree.SubElement(tag, 'AnimOrder').text = str(pat1section.animorder)
        etree.SubElement(tag, 'StartOfFile').text = str(pat1section.start)
        etree.SubElement(tag, 'EndOfFile').text = str(pat1section.end)
        etree.SubElement(tag, 'ChildBinding').text = str(pat1section.childbinding)
        etree.SubElement(tag, 'First').text = str(first)
        strngs2 = etree.SubElement(tag, 'AnimatedGroups')
        self.position = pat_start_pos + pat1section.secondsoffset
        for _ in range(pat1section.numseconds):
            group_name = self.unpackkvarstr()
            etree.SubElement(strngs2, 'Groupname').text = str(group_name)

        self.read_header()

    def write_pat1_xml(self, pat1):
        tag = etree.SubElement(self.newroot, 'tag', type='pat1')
        etree.SubElement(tag, 'AnimOrder').text = str(pat1.animorder)
        etree.SubElement(tag, 'StartOfFile').text = str(pat1.start)
        etree.SubElement(tag, 'EndOfFile').text = str(pat1.end)
        etree.SubElement(tag, 'ChildBinding').text = str(pat1.childbinding)
        etree.SubElement(tag, 'First').text = str(first)
        strngs2 = etree.SubElement(tag, 'AnimatedGroups')
        self.position = pat_start_pos + pat1section.secondsoffset
        for _ in range(pat1section.numseconds):
            group_name = self.unpackkvarstr()
            etree.SubElement(strngs2, 'Groupname').text = str(group_name)
        
    def read_pai1section(self):
        pai_start_pos = self.position - 4
        pai1section = types.pai1section_tup(*self.unpackk('IHBBHHI'))

        tag = etree.SubElement(self.newroot, 'tag', type='pai1')
        tag.attrib['framesize'] = str(pai1section.framesize)
        tag.attrib['flags'] = str(pai1section.flags)

        timgs_offsets = [ self.unpackk('I') for _ in range(pai1section.numtimgs) ]
        for timgs_offset in timgs_offsets:
            self.position = pai_start_pos + 20 + timgs_offset
            timgs = etree.SubElement(tag, 'timg')
            timgs.attrib['name'] = self.unpackkvarstr()

        self.position = pai_start_pos + pai1section.entryoffset
        pane_offsets = [ self.unpackk('I') for _ in range(pai1section.numentries) ]
        for pane_offset in pane_offsets:
            self.position = pai_start_pos + pane_offset
            pane = etree.SubElement(tag, 'pane')
            name = self.unpackkvarstr()
            entry = types.entry_tup(*self.unpackk('BBH'))

            pane.attrib['name'] = name
            pane.attrib['type'] = str(entry.is_material)

            tag_offsets = [ self.unpackk('I') for _ in range(entry.num_tags) ]
            for tag_offset in tag_offsets:
                self.position = pai_start_pos + pane_offset + tag_offset
                typetree = etree.SubElement(pane, 'tag')
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
                    self.position = tag_start_pos + tag_data_offset
                    tag_data = types.tag_data_tup(*self.unpackk('BBHHHI'))
                    try:
                        typename = types.typedict[tag_type][tag_data.type2]
                    except KeyError:
                        typename = str(tag_data.type2)

                    entry = etree.SubElement(typetree, 'entry')
                    entry.attrib['type1'] = str(tag_data.type1)
                    entry.attrib['type2'] = typename

                    if tag_data.datatype == 2:
                        self.triplet(tag_data.coordcount, entry)
                    elif tag_data.datatype == 1:
                        self.pair(tag_data.coordcount, entry)
    
    def triplet(self, count, entry):
        for _ in range(count):
            p1, p2, p3 = self.unpackk('3f')
            info = etree.SubElement(entry, 'triplet')
            etree.SubElement(info, 'frame').text = str(p1)
            etree.SubElement(info, 'value').text = str(p2)
            etree.SubElement(info, 'blend').text = str(p3)

    def pair(self, count, entry):
        for _ in range(count):
            p1, p2, p3 = self.unpackk('fHH')
            info = etree.SubElement(entry, 'pair')
            etree.SubElement(info, 'frame').text = str(p1)
            etree.SubElement(info, 'data2').text = str(p2)
            etree.SubElement(info, 'padding').text = str(p3)
