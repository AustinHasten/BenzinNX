import re
import sys
from . import types
from lxml import etree, objectify
from struct import unpack_from, calcsize

class ReadBflan(object):
    def __init__(self, data, output):
        self.data = data
        SE = objectify.SubElement
        self.position = 0
        header = self.read_header()
        pat = self.read_pat()
        pai = self.read_pai()

        rootxml = objectify.Element('xmflan')
        versionxml = SE(rootxml, 'version', Number=str(header['version']))
        patxml = SE(versionxml, 'tag', type='pat1')
        patxml.AnimOrder = pat['animorder']
        patxml.StartOfFile = pat['start']
        patxml.EndOfFile = pat['end']
        patxml.ChildBinding = pat['childbinding']
        patxml.First = pat['first']
        AnimatedGroups = SE(patxml, 'AnimatedGroups')
        AnimatedGroups.Groupname = pat['groupnames']
        paixml = SE(versionxml, 'tag', type='pai1')
        paixml.attrib['framesize'] = str(pai['framesize'])
        paixml.attrib['flags'] = str(pai['flags'])
        for timgname in pai['timgnames']:
            SE(paixml, 'timg', name=timgname)
        for pane in pai['panes']:
            panexml = SE(paixml, 'pane', name=pane['name'], type=str(pane['is_material']))
            for tag in pane['tags']:
                tagxml = SE(panexml, 'tag', type=tag['type'])
                for data in tag['datas']:
                    entryxml = SE(tagxml, 'entry', type1=str(data['type1']), type2=data['typename'])
                    for x in data['content']:
                        entryxml.append(x)
        etree.ElementTree(rootxml).write(output, pretty_print=True)
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
        header = dict()
        header['magic'] = self.unpackkstr(4)
        header['endian'] = self.unpackk('H')
        header['firstsectionoffsetree'] = self.unpackk('H')
        header['version'] = self.unpackk('H')
        header['pad1'] = self.unpackk('H')
        header['filesize'] = self.unpackk('I')
        header['sections'] = self.unpackk('H')
        header['pad2'] = self.unpackk('H')
        return header

    def read_pat(self):
        pat = dict()
        pat['start_pos'] = self.position
        pat['magic'] = self.unpackkstr(4)
        pat['length'] = self.unpackk('I')
        pat['animorder'] = self.unpackk('H')
        pat['numseconds'] = self.unpackk('H')
        pat['firstoffset'] = self.unpackk('I')
        pat['secondsoffset'] = self.unpackk('I')
        pat['start'] = self.unpackk('H')
        pat['end'] = self.unpackk('H')
        pat['childbinding'] = self.unpackk('B')
        pat['pad'] = self.unpackk('B')
        pat['pad1'] = self.unpackk('H')
        self.position = pat['start_pos'] + pat['firstoffset']
        pat['first'] = self.unpackkvarstr()
        self.position = pat['start_pos'] + pat['secondsoffset']
        pat['groupnames'] = [ self.unpackkvarstr() for _ in range(pat['numseconds']) ]
        return pat

    def read_pai(self):
        pai = dict()
        pai['start_pos'] = self.position
        pai['magic'] = self.unpackkstr(4)
        pai['length'] = self.unpackk('I')
        pai['framesize'] = self.unpackk('H')
        pai['flags'] = self.unpackk('B')
        pai['pad'] = self.unpackk('B')
        pai['numtimgs'] = self.unpackk('H')
        pai['numentries'] = self.unpackk('H')
        pai['entryoffset'] = self.unpackk('I')
        pai['timgs_offsets'] = [ self.unpackk('I') for _ in range(pai['numtimgs']) ]
        pai['timgnames'] = []
        for offset in pai['timgs_offsets']:
            self.position = pai['start_pos'] + 20 + offset
            pai['timgnames'].append(unpackkvarstr())
        self.position = pai['start_pos'] + pai['entryoffset']
        pai['pane_offsets'] = [ self.unpackk('I') for _ in range(pai['numentries']) ]
        pai['panes'] = [ self.read_pane(pai['start_pos'], offset) for offset in pai['pane_offsets'] ]
        return pai

    def read_pane(self, pai_start_pos, pane_offset):
        self.position = pai_start_pos + pane_offset
        pane = dict()
        pane['name'] = self.unpackkvarstr()
        pane['num_tags'] = self.unpackk('B')
        pane['is_material'] = self.unpackk('B')
        pane['pad'] = self.unpackk('H')
        pane['tag_offsets'] = [ self.unpackk('I') for _ in range(pane['num_tags']) ]
        pane['tags'] = [ self.read_tag(pai_start_pos, pane_offset, offset) for offset in pane['tag_offsets'] ]
        return pane

    def read_tag(self, pai_start_pos, pane_offset, tag_offset):
        self.position = pai_start_pos + pane_offset + tag_offset
        tag = dict()
        tag['start_pos'] = self.position
        tag['type'] = self.unpackkstr(4)
        if tag['type'] == ',\x00\x00\x00':
            tag['type'] = self.unpackkstr(4)
        tag['entry_count'] = self.unpackk('B')
        tag['pad'] = self.unpackk('3B')
        tag['data_offsets'] = [ self.unpackk('I') for _ in range(tag['entry_count']) ]
        tag['datas'] = [ self.read_tag_data(tag, offset) for offset in tag['data_offsets'] ]
        return tag

    def read_tag_data(self, tag, data_offset):
        self.position = tag['start_pos'] + data_offset
        data = dict()
        data['type1'] = self.unpackk('B')
        data['type2'] = self.unpackk('B')
        data['type'] = self.unpackk('H')
        data['coordcount'] = self.unpackk('H')
        data['pad1'] = self.unpackk('H')
        data['offsettotagdata'] = self.unpackk('I')
        try:
            data['typename'] = types.typedict[tag['type']][data['type2']]
        except KeyError:
            data['typename'] = str(data['type2'])
        data['content'] = []
        if data['type'] == 2:
            data['content'] = [ self.triplet() for _ in range(data['coordcount']) ]
        elif data['type'] == 1:
            data['content'] = [ self.pair() for _ in range(data['coordcount']) ]
        return data

    def triplet(self):
        info = objectify.Element('triplet')
        info.frame, info.value, info.blend = self.unpackk('3f')
        return info

    def pair(self):
        info = objectify.Element('pair')
        info.frame, info.data2, info.padding = self.unpackk('fHH')
        return info
