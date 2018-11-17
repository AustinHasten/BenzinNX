import sys
import struct
from . import types
from math import ceil

class WriteBflan(object):
    def by4(self, n):
        return (ceil(n / 4) * 4)

    def plusnull(self, length):
        return length + 1

    def represents_int(self, data, list):
        try:
            return int(data)
        except ValueError:
            try:
                return list.index(data)
            except:
                print(f'{data} is an unknown entry.')
                sys.exit(1)

    def start(self, data, name, output):
        self.file_sections = 0
        self.output_file = b''
        self.version = data.find('version')
        
        tags = self.version.findall('tag')
        routing = {'pat1':self.writepat1, 'pai1':self.writepai1}
        for tag in tags:
            self.output_file += routing[tag.get('type')](tag)
        
        # TODO Find exception for when the file is in use
        self.output_file = self.header() + self.output_file
        if not output:
            output = name + '.bflan'
        with open(output, 'wb') as dirpath:
            dirpath.write(self.output_file)
        print('File Converted')
        
    def header(self):
        return struct.pack('<4s4HI2H', b'FLAN', 65279, 20, int(self.version.get('Number')), 0, len(self.output_file) + 20, self.file_sections, 0)
            
    def writepat1(self, sec):
        data = list(sec)
        anim_order = int(data[0].text)
        start = int(data[1].text)
        end = int(data[2].text)
        child_binding = int(data[3].text)
        first = data[4].text
        if not first:
            first = ''
        first_offset = 28
        seconds_offset = self.by4(len(first)) + first_offset
        data2 = list(data[5])
        f_and_s = struct.pack('%ds'%self.by4(len(first)), str.encode(first))
        for entry in data2:
            f_and_s += struct.pack('<28s', str.encode(entry.text))
        
        temp_sec = struct.pack('<2H2I2H2BH', anim_order, len(data2), first_offset, seconds_offset, start, end, child_binding, 0, 0)
        temp_sec += f_and_s
        pat1sec = struct.pack('<4sI',str.encode(sec.get('type')) ,int(len(temp_sec))+8)
        pat1sec += temp_sec
        self.file_sections += 1        
        return pat1sec
        
    def writepai1(self, sec):
        framesize = sec.get('framesize')
        flags = sec.get('flags')
        timgs = sec.findall('timg')
        entries = sec.findall('pane')
        timg_sec = ''
        
        # Write timg section if there is one
        if len(timgs) != 0:
            timg_offset = [ 4 * len(timgs) ]
            timg_names = struct.pack('<%ds'%self.plusnull(len(timgs[0].get('name'))),timgs[0].get('name'))
    
            for i in range(1, len(timgs)):
                timg_offset.append(len(timg_names) + timg_offset[0])
                timg_names += struct.pack('<%ds'%self.plusnull(len(timgs[i].get('name'))),timgs[i].get('name'))
            
            while len(timg_names) % 4 != 0:
                timg_names += '\x00'
                
            timg_sec = struct.pack('<%sI' % len(timg_offset), *timg_offset)
            timg_sec += timg_names
            
        temp_sec = struct.pack('<H2B2HI', int(framesize), int(flags), 0, len(timgs), len(entries), len(timg_sec) + 20)
        temp_sec += str.encode(timg_sec)
        
        baselength = len(temp_sec) + 8
        entry_offsets = [4*len(entries) + baselength]
        pane_sec = self.pane_section(entries[0])
        for i in range(1, len(entries)):
            entry_offsets.append(len(pane_sec) + entry_offsets[0])
            pane_sec += self.pane_section(entries[i])
        
        temp_sec2 = struct.pack('<%sI' % len(entry_offsets), *entry_offsets)
        temp_sec2 += pane_sec
        temp_sec += temp_sec2        
        pai1sec = struct.pack('<4sI',str.encode(sec.get('type')), int(len(temp_sec))+8)
        pai1sec += temp_sec
        self.file_sections += 1
        return pai1sec
    
    
    def pane_section(self, pane):
        name = pane.get('name')
        tags = pane.findall('tag')
        is_material = pane.get('type')
        pane_sec = struct.pack('<28s2BH' , str.encode(name), len(tags), int(is_material), 0)
        
        tag_offsets = [4*len(tags) + len(pane_sec)]
        taginfo = self.tag_section(tags[0])
    
        for i in range(1, len(tags)):
            tag_offsets.append(len(taginfo) + tag_offsets[0])
            taginfo += self.tag_section(tags[i])
        
        temp_sec = struct.pack('<%sI' % len(tag_offsets), *tag_offsets)
        temp_sec += taginfo
        pane_sec += temp_sec
        return pane_sec
    
    def tag_section(self, tag):
        tagtype = tag.get('type').upper()
        entry_count = tag.findall('entry')
        taginfo = struct.pack('<4s4B' , str.encode(tagtype), len(entry_count), 0, 0, 0)
        
        info_offset = [4*len(entry_count) + len(taginfo)]
        entry_section = self.entry_section(entry_count[0], tagtype)
                
        for i in range(1, len(entry_count)):
            info_offset.append(len(entry_section) + info_offset[0])
            entry_section += self.entry_section(entry_count[i], tagtype)
        
        temp_sec = struct.pack('<%sI' % len(info_offset), *info_offset)
        temp_sec += entry_section
        taginfo += temp_sec
        return taginfo
    
    def entry_section(self, entry, tagtype):
        type1 = entry.get('type1')
        try:
            type2 = self.represents_int(entry.get('type2'), types.typedict[tagtype])
        except:
            print('entry section error', tagtype)
            sys.exit(1)
        
        if len(entry.findall('triplet')) != 0:
            data_type = 2
            coord_count = entry.findall('triplet')
            temp_sec = self.triplet(coord_count)
        elif len(entry.findall('pair')) != 0:
            data_type = 1
            coord_count = entry.findall('pair')
            temp_sec = self.pair(coord_count)
        
        entry_section = struct.pack('<2B3HI' , int(type1), int(type2), data_type, len(coord_count), 0, 12)
        entry_section += temp_sec
        return entry_section
    
    def triplet(self, count):
        temp_sec = b''
        for i in count:
            p1 = float(i[0].text)
            p2 = float(i[1].text)
            p3 = float(i[2].text)
            temp_sec += struct.pack('<3f' , p1, p2, p3)
        return temp_sec
        
    def pair(self, count):
        temp_sec = b''
        for i in count:
            p1 = float(i[0].text)
            p2 = int(i[1].text)
            p3 = int(i[2].text)
            temp_sec += struct.pack('<f2H' , p1, p2, p3)
        return temp_sec
